import pyblish.api
from grill_tools import pyblish_utils


# Pyblish callbacks for presisting instance states to the scene
def instance_toggled(instance, new_value, old_value):

    instance.data["instanceToggled"](instance, new_value)


def init():

    pyblish_utils.init()

    pyblish.api.register_callback("instanceToggled", instance_toggled)
