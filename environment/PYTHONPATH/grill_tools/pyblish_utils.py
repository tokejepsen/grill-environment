import os

from pyblish import api, util
import pyblish_qml
import pyblish_royalrender
from Qt import QtWidgets


def register_process_plugins():

    paths = []

    try:
        import pyblish_nuke
        paths.append(
            os.path.join(os.path.dirname(pyblish_nuke.__file__), "plugins")
        )
    except ImportError:
        pass

    try:
        import pyblish_nukeassist
        paths.append(
            os.path.join(
                os.path.dirname(pyblish_nukeassist.__file__), "plugins"
            )
        )
    except ImportError:
        pass

    try:
        import pyblish_maya
        paths.append(
            os.path.join(os.path.dirname(pyblish_maya.__file__), "plugins")
        )
    except ImportError:
        pass

    # process plugins
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
    feedback_context(context)


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
    feedback_context(context)


def feedback_context(context):

    header = "{:<40} -> {}".format("Plug-in", "Instance")
    result = "{plugin.__name__:<40} -> {instance}"
    error = "+-- EXCEPTION: {:<70}"
    error_results = list()
    results = list()
    errors = False
    for r in context.data["results"]:
        # Format exception (if any)
        if r["error"]:
            errors = True
            error_results.append(result.format(**r))
            error_results.append(error.format(r["error"]))

        if r["records"]:
            results.append(result.format(**r))

        for record in r["records"]:
            results.append(record.msg)

    error_report = "{header}\n{line}\n{results}".format(
        header=header, results="\n".join(error_results), line="-" * 70
    )
    report = "{header}\n{line}\n{results}".format(
        header=header, results="\n".join(results), line="-" * 70
    )

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
        messagebox.setDetailedText(error_report)
    else:
        messagebox.setText(
            "Process successfull."
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

    messagebox.exec_()


def init():

    # Register GUI
    api.register_gui("pyblish_lite")
    api.register_gui("pyblish_qml")

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
        settings.HiddenSections = [
            "Collect", "Other", "Extract", "Integrate", "output"
        ]
