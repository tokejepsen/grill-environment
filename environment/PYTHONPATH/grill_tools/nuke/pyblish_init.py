import nuke

from pyblish import api
from grill_tools import pyblish_utils


# Pyblish callbacks for presisting instance states to the scene
def instance_toggled(instance, new_value, old_value):

    instance.data["instanceToggled"](instance, new_value)


# Nuke callback for modifying the Write nodes on creation
def modify_write_node():

    # Setting the file path
    file_path = (
        "[python {nuke.script_directory()}]/workspace/[python "
        "{nuke.thisNode().name()}]/[python {os.path.splitext("
        "os.path.basename(nuke.scriptName()))[0]}]/[python {"
        "os.path.splitext(os.path.basename(nuke.scriptName()))[0]}]_"
        "[python {nuke.thisNode().name()}].%04d.exr"
    )

    nuke.thisNode()["file"].setValue(file_path)

    # Setting the file type
    nuke.thisNode()["file_type"].setValue("exr")

    # Setting metadata
    nuke.thisNode()["metadata"].setValue("all metadata")

    # Enable create directories if it exists.
    # Older version of Nuke does not have this option.
    if "create_directories" in nuke.thisNode().knobs():
        nuke.thisNode()["create_directories"].setValue(True)


# Nuke callback for modifying the WriteGeo nodes on creation
def modify_writegeo_node():

    # Setting the file path
    file_path = (
        "[python {nuke.script_directory()}]/workspace/[python "
        "{os.path.splitext(os.path.basename(nuke.scriptName()))[0]}]_"
        "[python {nuke.thisNode().name()}].abc"
    )

    nuke.thisNode()["file"].setValue(file_path)

    # Setting the file type
    nuke.thisNode()["file_type"].setValue("abc")


def init():

    pyblish_utils.init()

    # Register callbacks
    api.register_callback("instanceToggled", instance_toggled)

    # Adding menu items
    menubar = nuke.menu("Nuke")
    menu = menubar.menu("grill-tools")

    cmd = "from grill_tools import pyblish_utils;"
    cmd += "pyblish_utils.process_targets_all()"
    menu.addCommand("Process", cmd, index=0)

    cmd = "from grill_tools import pyblish_utils;"
    cmd += "pyblish_utils.process_targets_local()"
    menu.addCommand("Process Local", cmd, index=1)

    cmd = "from grill_tools import pyblish_utils;"
    cmd += "pyblish_utils.process_targets_local_silent()"
    menu.addCommand("Process Local silent", cmd, "ctrl+alt+1", index=2)

    cmd = "from grill_tools import pyblish_utils;"
    cmd += "pyblish_utils.process_targets_royalrender()"
    menu.addCommand("Process RoyalRender", cmd, index=3)

    cmd = "from grill_tools import pyblish_utils;"
    cmd += "pyblish_utils.process_targets_royalrender_silent()"
    menu.addCommand("Process RoyalRender silent", cmd, "ctrl+alt+2", index=4)

    menu.addSeparator(index=5)

    nuke.addOnUserCreate(modify_write_node, nodeClass="Write")
    nuke.addOnUserCreate(modify_writegeo_node, nodeClass="WriteGeo")
