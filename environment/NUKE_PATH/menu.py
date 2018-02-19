import os
import imp

import nuke

from grill_tools import pyblish_utils
from pyblish import api


pyblish_utils.init()

# Create menu
menubar = nuke.menu("Nuke")
menu = menubar.addMenu("grill-tools")

cmd = "from grill_tools import pyblish_utils;"
cmd += "pyblish_utils.process_targets_local()"
menu.addCommand("Process Local", cmd, index=0)

cmd = "from grill_tools import pyblish_utils;"
cmd += "pyblish_utils.process_targets_local_silent()"
menu.addCommand("Process Local silent", cmd, "ctrl+alt+1", index=1)

cmd = "from grill_tools import pyblish_utils;"
cmd += "pyblish_utils.process_targets_royalrender()"
menu.addCommand("Process RoyalRender", cmd, index=2)

cmd = "from grill_tools import pyblish_utils;"
cmd += "pyblish_utils.process_targets_royalrender_silent()"
menu.addCommand("Process RoyalRender silent", cmd, "ctrl+alt+2", index=3)

menu.addSeparator(index=4)

create_menu = menu.addMenu("Create")
create_menu.addCommand(
    "Write",
    "from grill_tools.nuke.node import create;create(\"Write\")"
)

tools_menu = menu.addMenu("Tools")
tools_menu.addCommand(
    "Workspace Loader",
    "from grill_tools.nuke import workspace_loader;workspace_loader.show()"
)
# Can't find any hotkey with "r" that isn't already taken. Hence "u".
tools_menu.addCommand(
    "Read from Write",
    "from grill_tools.nuke.read_from_write import ReadFromWrite;"
    "ReadFromWrite()",
    "u"
)
tools_menu.addCommand(
    "Open from Node",
    "from grill_tools.nuke import utils;utils.open_from_node()",
    "ctrl+shift+o"
)
tools_menu.addCommand(
    "Open with DJV",
    "from grill_tools.nuke import utils;utils.open_with_djv()",
    "ctrl+shift+d"
)
cmd = "from grill_tools.nuke import utils;"
cmd += "utils.createExrCamVray(nuke.selectedNode())"
tools_menu.addCommand("Camera From Vray EXR", cmd)
tools_menu.addCommand(
    "Write from Read",
    "from grill_tools.nuke import utils;utils.write_from_read()"
)
tools_menu.addCommand(
    "Metadata from Node",
    "from grill_tools.nuke import utils;utils.metadata_from_node()"
)
tools_menu.addCommand(
    "Slash Convert",
    "from grill_tools import slash_converter;slash_converter.show()"
)
tools_menu.addCommand(
    "Slash Convert Toggle",
    "from grill_tools import slash_converter;slash_converter.toggle()"
)


# Register callbacks
# Pyblish callbacks for presisting instance states to the scene
def instance_toggled(instance, new_value, old_value):

    instance.data["instanceToggled"](instance, new_value)


api.register_callback("instanceToggled", instance_toggled)


# Check frame range is locked when reading, since startup locking doesn't work
def modify_read_node():
    if not nuke.root()["lock_range"].getValue():
        print "Locking frame range."
        nuke.root()["lock_range"].setValue(True)


nuke.addOnUserCreate(modify_read_node, nodeClass="Read")


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

    # Setting autocrop
    nuke.thisNode()["autocrop"].setValue(True)

    # Enable create directories if it exists.
    # Older version of Nuke does not have this option.
    if "create_directories" in nuke.thisNode().knobs():
        nuke.thisNode()["create_directories"].setValue(True)


nuke.addOnUserCreate(modify_write_node, nodeClass="Write")


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


nuke.addOnUserCreate(modify_writegeo_node, nodeClass="WriteGeo")


# Nuke callback for changing the path extension when changing the file type
def file_type_changed():
    node = nuke.thisNode()
    knob = nuke.thisKnob()

    if knob.name() == "file_type":
        try:
            path = node["file"].value()
            node["file"].setValue(
                "{0}.{1}".format(os.path.splitext(path)[0], knob.value())
            )
        except:
            pass


nuke.addKnobChanged(file_type_changed, nodeClass="Write")

# Adding ftrack assets if import is available.
try:
    imp.find_module("ftrack_connect")
    imp.find_module("ftrack_connect_nuke")

    from grill_tools.nuke import ftrack_assets
    ftrack_assets.register_assets()
    from grill_tools.nuke import ftrack_init
    ftrack_init.init()
except ImportError as error:
    print "Could not find ftrack modules: " + str(error)
