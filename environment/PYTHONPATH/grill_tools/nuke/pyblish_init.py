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

    # Backdrop instances
    if "scene" == instance.data["family"]:
        if instance[0].Class() == "BackdropNode":
            for node in instance[0].getNodes():
                instance[0]["publish"].setValue(bool(new_value))
        return

    # All instances are nodes, except for the scene instance
    try:
        instance[0]["disable"].setValue(not bool(new_value))
    except:
        pass


def processing_target():
    import pyblish_qml

    pyblish_qml.show(targets=["processing"])


def init():

    # Register callbacks
    pyblish.api.register_callback("instanceToggled", custom_toggle_instance)

    # Register GUI
    pyblish.api.register_gui("pyblish_lite")
    pyblish.api.register_gui("pyblish_qml")

    # pyblish-qml settings
    try:
        __import__("pyblish_qml")
        __import__("Qt")
    except ImportError as e:
        print("grill-tools: Could not load pyblish-qml: %s " % e)
    else:
        from pyblish_qml import settings
        from Qt import QtWidgets

        app = QtWidgets.QApplication.instance()
        screen_resolution = app.desktop().screenGeometry()
        width, height = screen_resolution.width(), screen_resolution.height()
        settings.WindowSize = (width / 2, height - (height / 15))
        settings.WindowPosition = (0, 0)

        # Adding menu items
        menubar = nuke.menu("Nuke")
        menu = menubar.menu("grill-tools")

        cmd = "from grill_tools.nuke import pyblish_init;"
        cmd += "pyblish_init.processing_target()"
        menu.addCommand("Process...", cmd, index=0)
        menu.addSeparator(index=1)
