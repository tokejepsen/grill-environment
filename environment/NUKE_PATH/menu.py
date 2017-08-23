import imp

import nuke

from grill_tools.nuke import pyblish_init


# Create menu
menubar = nuke.menu("Nuke")
menu = menubar.addMenu("grill-tools")

menu.addCommand(
    "Workspace Loader",
    "from grill_tools.nuke import workspace_loader;workspace_loader.show()"
)
# Can't find any hotkey with "r" that isn't already taken. Hence "u".
menu.addCommand(
    "Read from Write",
    "from grill_tools.nuke.read_from_write import ReadFromWrite;"
    "ReadFromWrite()",
    "u"
)


# grill-tools callbacks
# Nuke callback for modifying the write nodes on creation
def modify_write_node():

    # Setting the file path
    file_path = (
        "[python {nuke.script_directory()}]/workspace/[python "
        "{nuke.thisNode()[\"name\"].getValue()}]/[python "
        "{os.path.splitext(os.path.basename(nuke.scriptName()))[0]}]_"
        "[python {nuke.thisNode()[\"name\"].getValue()}].%04d.exr"
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


nuke.addOnUserCreate(modify_write_node, nodeClass="Write")

# Setup for pyblish
pyblish_init.init()

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
