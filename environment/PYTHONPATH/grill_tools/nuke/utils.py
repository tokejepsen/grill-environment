import os
import webbrowser

import nuke


def open_from_node():
    for node in nuke.selectedNodes():
        path = nuke.filename(node)

        if path is None:
            continue

        webbrowser.open("file://{0}".format(os.path.dirname(path)))
