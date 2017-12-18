import pyblish.api
from grill_tools import pyblish_utils


# Pyblish callbacks for presisting instance states to the scene
def instance_toggled(instance, new_value, old_value):

    instance.data["instanceToggled"](instance, new_value)


def init():

    pyblish_utils.init()

    pyblish.api.register_callback("instanceToggled", instance_toggled)

    # pyblish-qml settings
    try:
        __import__("pyblish_qml")
    except ImportError as e:
        print("grill-tools: Could not load pyblish-qml: %s " % e)
    else:
        from pyblish_qml import settings
        settings.HiddenSections = [
            "Collect", "Other", "Integrate", "output"
        ]
