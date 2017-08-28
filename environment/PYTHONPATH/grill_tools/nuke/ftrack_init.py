import os

import nuke

import ftrack_api
from ftrack_connect_nuke.ui.legacy import scan_for_new_assets
from grill_tools.nuke import ftrack_utils
from Qt import QtWidgets


def project_settings_init():

    session = ftrack_api.Session()
    task = session.get("Task", os.environ["FTRACK_TASKID"])

    changes = []

    # FPS
    local_fps = remote_fps = nuke.root()["fps"].getValue()
    if "fps" in task["parent"]["custom_attributes"]:
        remote_fps = task["parent"]["custom_attributes"]["fps"]

    if local_fps != remote_fps:
        changes.append(
            {
                "setting": nuke.root()["fps"],
                "new": remote_fps,
                "old": local_fps
            }
        )

    # Resolution
    local_width = remote_width = nuke.root()["format"].value().width()
    if "width" in task["parent"]["custom_attributes"]:
        remote_width = int(task["parent"]["custom_attributes"]["width"])
    local_height = remote_height = nuke.root()["format"].value().height()
    if "height" in task["parent"]["custom_attributes"]:
        remote_height = int(task["parent"]["custom_attributes"]["height"])

    if (remote_width and remote_height and remote_width != local_width or
       remote_height != local_height):

        fmt = None
        for f in nuke.formats():
            if f.width() == remote_width and f.height() == remote_height:
                fmt = f.name()

        if not fmt:
            nuke.addFormat(
                "{0} {1} FtrackDefault".format(
                    int(remote_width), int(remote_height)
                )
            )
            fmt = "FtrackDefault"

        changes.append(
            {
                "setting": nuke.root()["format"],
                "new": fmt,
                "old": nuke.root()["format"].value().name()
            }
        )

    # Frame Range
    handles = 0
    if "handles" in task["parent"]["custom_attributes"]:
        handles = task["parent"]["custom_attributes"]["handles"]
    local_fstart = remote_fstart = nuke.root()["first_frame"].getValue()
    if "fstart" in task["parent"]["custom_attributes"]:
        remote_fstart = task["parent"]["custom_attributes"]["fstart"]
        remote_fstart -= handles
    local_fend = remote_fend = nuke.root()["last_frame"].getValue()
    if "fend" in task["parent"]["custom_attributes"]:
        remote_fend = task["parent"]["custom_attributes"]["fend"]
        remote_fend += handles

    if local_fstart != remote_fstart:
        changes.append(
            {
                "setting": nuke.root()["first_frame"],
                "new": remote_fstart,
                "old": local_fstart
            }
        )

    if local_fend != remote_fend:
        changes.append(
            {
                "setting": nuke.root()["last_frame"],
                "new": remote_fend,
                "old": local_fend
            }
        )

    # No changes.
    if not changes:
        return

    # Display changes to user
    messagebox = QtWidgets.QMessageBox()
    messagebox.setIcon(messagebox.Warning)

    messagebox.setWindowTitle("Project Setting Changes")
    messagebox.setText(
        "Changes to the project settings has been detected in Ftrack."
    )

    detailed_text = ""
    for change in changes:
        detailed_text += '"{0}": {1} > {2}\n'.format(
            change["setting"].name(), change["old"], change["new"]
        )
    messagebox.setDetailedText(detailed_text)

    messagebox.setStandardButtons(messagebox.Ok)
    messagebox.addButton(messagebox.Cancel)
    result = messagebox.exec_()

    # Cancel changes
    if result == QtWidgets.QMessageBox.Cancel:
        return

    # Set changes.
    for change in changes:
        change["setting"].setValue(change["new"])


def lut_init():

    # Check to see if launched from a task.
    if "FTRACK_TASKID" not in os.environ:
        return

    # Get published LUT, either on the current task or through parents.
    session = ftrack_api.Session()

    query = "Component where version.task_id is \"{0}\""
    query += " and version.asset.type.short is \"lut\""
    components = session.query(
        query.format(os.environ["FTRACK_TASKID"])
    )

    if not components:
        task = session.get("Task", os.environ["FTRACK_TASKID"])
        query = "Component where version.asset.type.short is \"lut\""
        query += " and version.asset.parent.id is \"{0}\""
        for item in reversed(task["link"][:-1]):
            components = session.query(
                query.format(item["id"])
            )
            if components:
                break

    version = 0
    component = None
    for c in components:
        if c["version"]["version"] > version:
            component = c
            version = c["version"]["version"]

    if not component:
        print "{0}: Could not find any published LUTs.".format(__file__)
        return

    # Collect component data and Nuke display name.
    path = component["component_locations"][0]["resource_identifier"]

    display_name = ""
    for item in component["version"]["task"]["link"][:]:
        display_name += session.get(item["type"], item["id"])["name"] + "/"
    display_name += "v" + str(version).zfill(3)

    # Register the lut file.
    nuke.ViewerProcess.register(
        display_name, nuke.createNode, (path.replace("\\", "/"), "")
    )

    # Adding viewerprocess callback
    nuke.addOnCreate(
        modify_viewer_node, args=(display_name), nodeClass="Viewer"
    )


# Nuke callback for modifying the viewer node on creation
def modify_viewer_node(viewerprocess):

    nuke.thisNode()["viewerProcess"].setValue(str(viewerprocess))


def init():

    # Check to see if launched from a task.
    if "FTRACK_TASKID" not in os.environ:
        return

    # Adding menu items
    menubar = nuke.menu("Nuke")
    menu = menubar.menu("grill-tools")
    cmd = "from grill_tools.nuke import ftrack_utils;"
    cmd += "ftrack_utils.scan_for_unused_components()"
    menu.addCommand("Scan for unused components", cmd)

    cmd = "from grill_tools.nuke import ftrack_utils;"
    cmd += "ftrack_utils.import_all_image_sequences()"
    menu.addCommand("Import All Image Sequences", cmd)

    cmd = "from grill_tools.nuke import ftrack_utils;"
    cmd += "ftrack_utils.import_all_gizmos()"
    menu.addCommand("Import All Gizmos", cmd)

    # Adding published LUT
    lut_init()

    # grill-tools callbacks
    nuke.addOnScriptLoad(project_settings_init)
    nuke.addOnScriptLoad(ftrack_utils.scan_for_unused_components)

    # Scan explicitly for new assets on startup,
    # since Ftrack native implementation only scans
    # when loading a script within Nuke.
    nuke.addOnScriptLoad(scan_for_new_assets)

    # pyblish-qml settings
    try:
        __import__("pyblish_qml")
    except ImportError as e:
        print("grill-tools: Could not load pyblish-qml: %s " % e)
    else:
        from pyblish_qml import settings

        # Check to see if launched from a task.
        if "FTRACK_TASKID" not in os.environ:
            return

        session = ftrack_api.Session()
        task = session.get("Task", os.environ["FTRACK_TASKID"])
        ftrack_path = ""
        for item in task["link"]:
            ftrack_path += session.get(item["type"], item["id"])["name"]
            ftrack_path += " / "
        settings.WindowTitle = ftrack_path[:-3]
