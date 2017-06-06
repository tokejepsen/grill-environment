import imp

import nuke

import pyblish.api


# Pyblish callbacks for presisting instance states to the scene
def custom_toggle_instance(instance, new_value, old_value):

    if "gizmo" in instance.data["families"]:
        instance[0]["gizmo"].setValue(bool(new_value))
        return

    if "lut" in instance.data["families"]:
        instance[0]["lut"].setValue(bool(new_value))
        return

    # All instances are nodes, except for the scene instance
    try:
        instance[0]["disable"].setValue(not bool(new_value))
    except:
        pass


pyblish.api.register_callback("instanceToggled", custom_toggle_instance)

# Register GUI
pyblish.api.register_gui("pyblish_lite")
pyblish.api.register_gui("pyblish_qml")

# pyblish-qml settings
try:
    __import__("pyblish_qml")
except ImportError as e:
    print("grill-tools: Could not load pyblish-qml: %s " % e)
else:
    from pyblish_qml import settings
    settings.WindowSize = (800, 600)

# Create menu
menubar = nuke.menu("Nuke")
menu = menubar.addMenu("grill-tools")

cmd = "from grill_tools.nuke import processing_location;"
cmd += "processing_location.show()"
menu.addCommand("Processing Location", cmd)

cmd = "from grill_tools.nuke import workspace_loader;"
cmd += "workspace_loader.show()"
menu.addCommand("Workspace Loader", cmd)


# grill-tools callbacks
# Nuke callback for modifying the write nodes on creation
def modify_write_node():

    # Setting the file path
    file_path = "[python {nuke.script_directory()}]/workspace/"
    file_path += "[python {nuke.thisNode()[\"name\"].getValue()}]/"
    file_path += "[python {os.path.splitext(os.path.basename("
    file_path += "nuke.scriptName()))[0]}].%04d.exr"

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

# Adding ftrack assets if import is available.
try:
    imp.find_module("ftrack_connect")
    imp.find_module("ftrack_connect_nuke")

    import ftrack_assets
    ftrack_assets.register_assets()
    import ftrack_init
    ftrack_init.init()
except ImportError as error:
    print "Could not find ftrack modules: " + str(error)
