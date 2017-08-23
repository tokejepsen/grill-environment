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


def processing_targets_all():
    import os
    import pyblish.api
    import pyblish_qml
    import pyblish_royalrender
    import pyblish_nuke

    pyblish.api.deregister_all_plugins()

    # Processing plugins
    paths = []
    paths.append(
        os.path.join(os.path.dirname(pyblish_nuke.__file__), "plugins")
    )
    for plugin in pyblish.api.discover(paths=paths):
        SubClass = type(
            plugin.__name__ + "Processing",
            (plugin,),
            {'targets': ["processing"]}
        )
        pyblish.api.register_plugin(SubClass)

    # RoyalRender plugins
    paths = []
    paths.append(
        os.path.join(os.path.dirname(pyblish_royalrender.__file__), "plugins")
    )
    for plugin in pyblish.api.discover(paths=paths):
        SubClass = type(
            plugin.__name__ + "Processing",
            (plugin,),
            {'targets': ["processing.royalrender"]}
        )
        pyblish.api.register_plugin(SubClass)

    pyblish_qml.show(
        targets=["processing", "processing.local", "processing.royalrender"]
    )


def processing_targets_local():
    import os
    import pyblish.api
    import pyblish_qml
    import pyblish_nuke

    pyblish.api.deregister_all_plugins()

    # Processing plugins
    paths = []
    paths.append(
        os.path.join(os.path.dirname(pyblish_nuke.__file__), "plugins")
    )
    for plugin in pyblish.api.discover(paths=paths):
        SubClass = type(
            plugin.__name__ + "Processing",
            (plugin,),
            {'targets': ["processing"]}
        )
        pyblish.api.register_plugin(SubClass)

    pyblish_qml.show(targets=["processing", "processing.local"])


def processing_targets_royalrender():
    import os
    import pyblish.api
    import pyblish_qml
    import pyblish_royalrender
    import pyblish_nuke

    pyblish.api.deregister_all_plugins()

    # Processing plugins
    paths = []
    paths.append(
        os.path.join(os.path.dirname(pyblish_nuke.__file__), "plugins")
    )
    for plugin in pyblish.api.discover(paths=paths):
        SubClass = type(
            plugin.__name__ + "Processing",
            (plugin,),
            {'targets': ["processing"]}
        )
        pyblish.api.register_plugin(SubClass)

    # RoyalRender plugins
    paths = []
    paths.append(
        os.path.join(os.path.dirname(pyblish_royalrender.__file__), "plugins")
    )
    for plugin in pyblish.api.discover(paths=paths):
        SubClass = type(
            plugin.__name__ + "Processing",
            (plugin,),
            {'targets': ["processing.royalrender"]}
        )
        pyblish.api.register_plugin(SubClass)

    pyblish_qml.show(targets=["processing", "processing.royalrender"])


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
        cmd += "pyblish_init.processing_targets_all()"
        menu.addCommand("Process...", cmd, index=0)
        cmd = "from grill_tools.nuke import pyblish_init;"
        cmd += "pyblish_init.processing_targets_local()"
        menu.addCommand("Process Local...", cmd, index=1)
        cmd = "from grill_tools.nuke import pyblish_init;"
        cmd += "pyblish_init.processing_targets_royalrender()"
        menu.addCommand("Process RoyalRender...", cmd, index=2)
        menu.addSeparator(index=3)
