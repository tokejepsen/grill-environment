import pyblish.api
from grill_tools import pyblish_utils


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

    pyblish_utils.init()

    pyblish.api.register_callback("instanceToggled", toggle_instance)
