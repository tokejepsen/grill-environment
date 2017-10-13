import pyblish.api
from Qt import QtWidgets


# Pyblish callbacks for presisting instance states to the scene.
def toggle_instance(instance, new_value, old_value):

    node = instance[0]

    families = instance.data.get("families", [])
    if "cache" in families or "scene" in families:
        attrs = []
        for attr in node.listAttr(userDefined=True):
            attrs.append(attr.name(includeNode=False))

        attr_list = list(set(attrs) & set(families))

        if attr_list:
            node.attr(attr_list[0]).set(new_value)

    if "renderlayer" in instance.data.get("families", []):

        node.renderable.set(new_value)

    if "playblast" in instance.data.get("families", []):

        node.getTransform().publish.set(new_value)

    if "file" in instance.data.get("families", []):

        node.publish.set(new_value)


def init():

    pyblish.api.register_callback("instanceToggled", toggle_instance)

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
        app = QtWidgets.QApplication.instance()
        screen_resolution = app.desktop().screenGeometry()
        width, height = screen_resolution.width(), screen_resolution.height()
        settings.WindowSize = (width / 2, height - (height / 15))
        settings.WindowPosition = (0, 0)
