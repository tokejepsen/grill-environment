import os
import operator

import nuke

import ftrack_api
import ftrack_connect
from ftrack_connect.connector import FTAssetObject, HelpFunctions
from ftrack_connect_nuke.connector import Connector
from Qt import QtGui, QtWidgets, QtCore


class ProgressBar(QtWidgets.QWidget):
    """Progess bar for publishing."""

    def __init__(self, parent=None):
        super(ProgressBar, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint
        )

        layout = QtWidgets.QVBoxLayout(self)
        self.bar = QtGui.QProgressBar()
        layout.addWidget(self.bar)

        # Center widget on screen
        self.resize(500, 500)


def import_all_image_sequences():

    session = ftrack_connect.session.get_shared_session()
    task = session.query(
        'select parent.id from Task '
        'where id is "{0}"'.format(os.environ["FTRACK_TASKID"])
    ).one()
    versions = session.query(
        'select id from AssetVersion where asset.parent.id is "{0}" and'
        ' asset.type.short is "img"'.format(task["parent"]["id"])
    )

    scene_ids = []
    for version in get_scene_versions():
        scene_ids.append(version["id"])

    # Collect all components.
    components = []
    for version in get_latest_versions(versions):
        # Skip asset in scene
        if version["id"] in scene_ids:
            continue

        # Only import "main" components
        for component in version["components"]:
            if component["name"] == "main":
                components.append(component)

    progress_bar = ProgressBar()
    progress_bar.show()
    for progress in import_components(components):
        progress_bar.bar.setValue(progress * 100)

    progress_bar.deleteLater()


def import_all_gizmos():

    session = ftrack_connect.session.get_shared_session()
    task = session.query(
        'select parent.id from Task '
        'where id is "{0}"'.format(os.environ["FTRACK_TASKID"])
    ).one()
    versions = session.query(
        'AssetVersion where asset.parent.id is "{0}" and'
        ' asset.type.short is "nuke_gizmo"'.format(task["parent"]["id"])
    )

    # Collect all components.
    components = []
    for version in get_latest_versions(versions):
        components.extend(version["components"])

    # Collect all new components
    new_components = []
    for component in components:
        node_exists = nuke.exists(
            HelpFunctions.safeString(component["version"]["asset"]["name"]) +
            "_" + HelpFunctions.safeString(component["name"])
        )
        if not node_exists:
            new_components.append(component)

    progress_bar = ProgressBar()
    progress_bar.show()
    for progress in import_components(components):
        progress_bar.bar.setValue(progress * 100)

    progress_bar.deleteLater()


def get_latest_versions(versions):
    """Groups versions based on their asset id, and get the latest version."""

    data = {}
    for version in versions:
        asset_id = version["asset"]["id"]
        if asset_id in data.keys():
            if version["version"] > data[asset_id]["version"]:
                data[asset_id] = version
        else:
            data[asset_id] = version

    return data.values()


def import_components(components):
    """Import components with host plugins iterator."""

    locations = {}
    session = ftrack_connect.session.get_shared_session()
    for location in session.query("select id from Location"):
        locations[location["id"]] = location

    connector = Connector()
    progress = 0
    for component in components:
        try:
            location_id = max(
                component.get_availability().iteritems(),
                key=operator.itemgetter(1)
            )[0]
            file_path = locations[location_id].get_resource_identifier(
                component
            )

            asset = FTAssetObject(
                    componentId=component['id'],
                    filePath=file_path,
                    componentName=component['name'],
                    assetVersionId=component["version"]["id"],
                    options={}
            )

            connector.importAsset(asset)
            progress += 1.0 / len(components)
            yield progress
        except ftrack_api.exception.ComponentNotInLocationError:
            pass


def get_unused_components():

    # Get scene data
    component_names = []
    asset_ids = []
    for node in nuke.allNodes():
        knobs = node.knobs()
        if "assetId" in knobs:
            asset_ids.append(node["assetId"].getValue())
        if "componentName" in knobs:
            component_names.append(node["componentName"].getValue())

    # Skip if no existing assets are found
    if not component_names:
        return []

    # Get all online components
    query = "Component where version.asset.id in ("
    for id in asset_ids:
        query += "\"{0}\",".format(id)
    query = query[:-1] + ")"

    data = {}
    components_data = {}
    session = ftrack_connect.session.get_shared_session()
    for component in session.query(query):
        name = component["name"]

        # Skip components used in scene
        if name in component_names:
            continue

        # Skip versions that are lower than existing ones
        version = component["version"]["version"]
        if name in data and version < data[name]:
            continue

        data[name] = version

        # Overwrite with higher version components
        components_data[name] = component

    # Flatten component data to a list
    components = []
    for component in components_data.itervalues():
        components.append(component)

    return components


def get_scene_versions():

    session = ftrack_connect.session.get_shared_session()

    versions = []
    for node in nuke.allNodes():
        knobs = node.knobs()
        if "assetId" in knobs and "componentName" in knobs:
            entity_id = (
                node["assetVersionId"].getValue().split("/")[-1].split("?")[0]
            )
            entity = session.query(
                'AssetVersion where id is "{0}"'.format(entity_id)
            ).first()
            if entity:
                versions.append(entity)

    return versions


def get_unused_version_components(asset_type):
    session = ftrack_connect.session.get_shared_session()
    scene_versions = get_scene_versions()
    versions = []
    scene_assets = []
    for version in scene_versions:
        scene_assets.append(version["asset"])
        versions.extend(
            session.query(
                'AssetVersion where task.id is "{0}" and asset.type.short is '
                '"{1}"'.format(version["task"]["id"], asset_type)
            )
        )

    components = []
    for version in get_latest_versions(versions):
        if version["asset"] in scene_assets:
            continue

        components.extend(version["components"])

    return components


def scan_for_unused_components():

    # Get components
    session = ftrack_connect.session.get_shared_session()
    components = get_unused_components()
    components.extend(get_unused_version_components("img"))
    if not components:
        return

    # Get details about components
    msg = ""
    msg_template = "task: {0}\nasset: {1}\nversion: {2}"
    msg_template += "\ncomponent: {3}\n\n"
    for component in components:

        # Getting Ftrack task path
        path = ""
        task = component["version"]["task"]
        for item in component["version"]["task"]["link"][:-1]:
            path += session.get(item["type"], item["id"])["name"] + "/"
        path += task["name"]

        # Adding component details
        msg += msg_template.format(
            path,
            component["version"]["asset"]["name"],
            component["version"]["version"],
            component["name"]
        )

    # Create message box
    msgBox = QtGui.QMessageBox()
    msgBox.setText("Unused components found.")
    msgBox.setDetailedText(msg)
    msgBox.setStandardButtons(
        QtGui.QMessageBox.Save | QtGui.QMessageBox.Cancel
    )
    msgBox.setDefaultButton(QtGui.QMessageBox.Save)
    button = msgBox.button(QtGui.QMessageBox.Save)
    button.setText("Import All")
    ret = msgBox.exec_()

    # Import components on request
    if ret == QtGui.QMessageBox.Save:
        import_components(components)


def setup():
    """Import exported scripts from NukeStudio."""

    session = ftrack_connect.session.get_shared_session()
    task = session.get("Task", os.environ["FTRACK_TASKID"])
    components = session.query(
        'Component where version.task.parent.id is_not "{0}" and '
        'version.asset.parent.id is "{0}" and version.asset.type.short is '
        '"scene"'.format(task["parent"]["id"])
    )

    max_version = 0
    latest_component = None
    for component in components:
        if max_version < component["version"]["version"]:
            max_version = component["version"]["version"]
            latest_component = component

    if latest_component:
        import_components([latest_component])
