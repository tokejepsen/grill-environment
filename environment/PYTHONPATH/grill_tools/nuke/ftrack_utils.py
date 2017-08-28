import os
import operator

import nuke

import ftrack_connect
from ftrack_connect.connector import FTAssetObject, HelpFunctions
from ftrack_connect_nuke.connector import Connector
from Qt import QtGui, QtWidgets


class Window(QtWidgets.QDialog):

    def __init__(self, title):
        super(Window, self).__init__()

        layout = QtWidgets.QHBoxLayout()
        app = QtWidgets.QApplication.instance()
        screen_resolution = app.desktop().screenGeometry()
        s_width, s_height = (
            screen_resolution.width(), screen_resolution.height()
        )
        width = 400
        self.setGeometry((s_width / 2) - (width / 2), s_height / 2, width, 0)
        self.setWindowTitle(title)
        self.setLayout(layout)
        self.show()


def import_all_image_sequences():

    win = Window("Importing all image sequences...")

    session = ftrack_connect.session.get_shared_session()
    task = session.query(
        'select parent.id from Task '
        'where id is "{0}"'.format(os.environ["FTRACK_TASKID"])
    ).one()
    versions = session.query(
        'AssetVersion where asset.parent.id is "{0}" and'
        ' asset.type.short is "img"'.format(task["parent"]["id"])
    )

    # Collect all components.
    components = []
    for version in get_latest_versions(versions):
        components.extend(version["components"])

    import_components(components)

    win.deleteLater()


def import_all_gizmos():

    win = Window("Importing all gizmos...")

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

    import_components(new_components)

    win.deleteLater()


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

    locations = {}
    session = ftrack_connect.session.get_shared_session()
    for location in session.query("select id from Location"):
        locations[location["id"]] = location

    connector = Connector()
    for component in components:
        location_id = max(
            component.get_availability().iteritems(),
            key=operator.itemgetter(1)
        )[0]
        file_path = locations[location_id].get_resource_identifier(component)

        asset = FTAssetObject(
                componentId=component['id'],
                filePath=file_path,
                componentName=component['name'],
                assetVersionId=component["version"]["id"],
                options={}
        )

        connector.importAsset(asset)


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
