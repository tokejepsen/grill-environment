import os

import nuke

from pyblish import api, util
import pyblish_qml
import pyblish_royalrender
import pyblish_nuke
from pyblish_qml import settings
from Qt import QtWidgets


# Pyblish callbacks for presisting instance states to the scene
def instance_toggled(instance, new_value, old_value):

    instance.data["instanceToggled"](instance, new_value)


def register_process_plugins():

    # process plugins
    paths = [
        os.path.join(os.path.dirname(pyblish_nuke.__file__), "plugins")
    ]
    for plugin in api.discover(paths=paths):
        SubClass = type(
            plugin.__name__ + "process",
            (plugin,),
            {'targets': ["process"]}
        )
        api.register_plugin(SubClass)


def register_process_royalrender_plugins():

    # RoyalRender plugins
    paths = [
        os.path.join(os.path.dirname(pyblish_royalrender.__file__), "plugins")
    ]
    for plugin in api.discover(paths=paths):
        SubClass = type(
            plugin.__name__ + "process",
            (plugin,),
            {'targets': ["process.royalrender"]}
        )
        api.register_plugin(SubClass)


def process_targets_all():

    api.deregister_all_plugins()

    register_process_plugins()
    register_process_royalrender_plugins()

    pyblish_qml.show(
        targets=["process", "process.local", "process.royalrender"]
    )


def process_targets_local():

    api.deregister_all_plugins()

    register_process_plugins()

    pyblish_qml.show(targets=["process", "process.local"])


def process_targets_local_silent():

    api.deregister_all_plugins()
    register_process_plugins()

    context = util.publish(targets=["process", "process.local"])
    feedback_context_success(context)


def process_targets_royalrender():

    api.deregister_all_plugins()

    register_process_plugins()
    register_process_royalrender_plugins()

    pyblish_qml.show(targets=["process", "process.royalrender"])


def process_targets_royalrender_silent():

    api.deregister_all_plugins()

    register_process_plugins()
    register_process_royalrender_plugins()

    context = util.publish(targets=["process", "process.royalrender"])
    feedback_context_success(context)


def feedback_context_success(context):

    header = "{:<40} -> {}".format("Plug-in", "Instance")
    result = "{plugin.__name__:<40} -> {instance}"
    error = "+-- EXCEPTION: {:<70}"
    results = list()
    errors = False
    for r in context.data["results"]:
        # Format exception (if any)
        if r["error"]:
            errors = True
            results.append(result.format(**r))
            results.append(error.format(r["error"]))

    report = "{header}\n{line}\n{results}".format(
        header=header, results="\n".join(results), line="-" * 70
    )

    # Display changes to user
    parent = None
    current = QtWidgets.QApplication.activeWindow()
    while current:
        parent = current
        current = parent.parent()

    messagebox = QtWidgets.QMessageBox(parent)
    messagebox.setWindowTitle("Process")
    messagebox.setStandardButtons(messagebox.Ok)

    if errors:
        messagebox.setIcon(messagebox.Warning)
        messagebox.setText(
            "Errors when trying to process."
        )
        messagebox.setDetailedText(report)

        spacer = QtWidgets.QWidget()
        spacer.setMinimumSize(400, 0)
        spacer.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding
        )

        layout = messagebox.layout()
        layout.addWidget(spacer, layout.rowCount(), 0, 1, layout.columnCount())
    else:
        messagebox.setText(
            "Process successfull."
        )

    messagebox.exec_()


# Nuke callback for modifying the Write nodes on creation
def modify_write_node():

    # Setting the file path
    file_path = (
        "[python {nuke.script_directory()}]/workspace/[python "
        "{nuke.thisNode().name()}]/[python {os.path.splitext("
        "os.path.basename(nuke.scriptName()))[0]}]/[python {"
        "os.path.splitext(os.path.basename(nuke.scriptName()))[0]}]_"
        "[python {nuke.thisNode().name()}].%04d.exr"
    )

    nuke.thisNode()["file"].setValue(file_path)

    # Setting the file type
    nuke.thisNode()["file_type"].setValue("exr")

    # Setting metadata
    nuke.thisNode()["metadata"].setValue("all metadata")

    # Enable create directories if it exists.
    # Older version of Nuke does not have this option.
    if "create_directories" in nuke.thisNode().knobs():
        nuke.thisNode()["create_directories"].setValue(True)


# Nuke callback for modifying the WriteGeo nodes on creation
def modify_writegeo_node():

    # Setting the file path
    file_path = (
        "[python {nuke.script_directory()}]/workspace/[python "
        "{os.path.splitext(os.path.basename(nuke.scriptName()))[0]}]_"
        "[python {nuke.thisNode().name()}].abc"
    )

    nuke.thisNode()["file"].setValue(file_path)

    # Setting the file type
    nuke.thisNode()["file_type"].setValue("abc")


def init():

    # Register callbacks
    api.register_callback("instanceToggled", instance_toggled)

    # Register GUI
    api.register_gui("pyblish_lite")
    api.register_gui("pyblish_qml")

    # pyblish-qml settings
    app = QtWidgets.QApplication.instance()
    screen_resolution = app.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()
    settings.WindowSize = (width / 2, height - (height / 15))
    settings.WindowPosition = (0, 0)

    # Adding menu items
    menubar = nuke.menu("Nuke")
    menu = menubar.menu("grill-tools")

    cmd = "from grill_tools.nuke import pyblish_init;"
    cmd += "pyblish_init.process_targets_all()"
    menu.addCommand("Process...", cmd, index=0)

    cmd = "from grill_tools.nuke import pyblish_init;"
    cmd += "pyblish_init.process_targets_local()"
    menu.addCommand("Process Local...", cmd, index=1)

    cmd = "from grill_tools.nuke import pyblish_init;"
    cmd += "pyblish_init.process_targets_local_silent()"
    menu.addCommand("Process Local silent...", cmd, "ctrl+1", index=2)

    cmd = "from grill_tools.nuke import pyblish_init;"
    cmd += "pyblish_init.process_targets_royalrender()"
    menu.addCommand("Process RoyalRender...", cmd, index=3)

    cmd = "from grill_tools.nuke import pyblish_init;"
    cmd += "pyblish_init.process_targets_royalrender_silent()"
    menu.addCommand("Process RoyalRender silent...", cmd, "ctrl+2", index=4)

    menu.addSeparator(index=5)

    nuke.addOnUserCreate(modify_write_node, nodeClass="Write")
    nuke.addOnUserCreate(modify_writegeo_node, nodeClass="WriteGeo")
