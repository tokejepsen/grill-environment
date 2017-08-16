import nuke

from Qt import QtGui
from grill_tools import workspace_loader


def import_img(instance):

    # Create read node
    node = nuke.createNode("Read", inpanel=False)

    # Set file path
    file_path = instance.data["collection"].format("{head}{padding}{tail}")
    node["file"].setValue(file_path)

    # Set range
    start = min(instance.data["collection"].indexes)
    end = max(instance.data["collection"].indexes)
    node["first"].setValue(start)
    node["origfirst"].setValue(start)
    node["last"].setValue(end)
    node["origlast"].setValue(end)


def application_function(instance):

    if "img" in instance.data["families"]:
        import_img(instance)
        return

    raise ValueError("Instance not supported.")


def show():

    main_window = QtGui.QApplication.activeWindow()
    win = workspace_loader.Window(main_window)

    win.application_function = application_function

    win.show()
