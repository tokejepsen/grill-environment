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
menu.addCommand(
    "Open from Node",
    "from grill_tools.nuke import utils;utils.open_from_node()",
    "ctrl+shift+o"
)
menu.addCommand(
    "Open with DJV",
    "from grill_tools.nuke import utils;utils.open_with_djv()",
    "ctrl+shift+d"
)

# Setup for pyblish
pyblish_init.init()


# Check frame range is locked when reading, since startup locking doesn't work
def modify_read_node():
    if not nuke.root()["lock_range"].getValue():
        print "Locking frame range."
        nuke.root()["lock_range"].setValue(True)


nuke.addOnUserCreate(modify_read_node, nodeClass="Read")


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
