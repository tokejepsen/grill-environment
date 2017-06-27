import imp

import pyblish.api


# Register GUI
pyblish.api.register_gui("pyblish_lite")
pyblish.api.register_gui("pyblish_qml")


# Adding ftrack assets if import is available.
try:
    imp.find_module("ftrack_connect_nuke_studio")

    from grill_tools.hiero import ftrack_init
    ftrack_init.init()
except ImportError as error:
    print "Could not find ftrack modules: " + str(error)
