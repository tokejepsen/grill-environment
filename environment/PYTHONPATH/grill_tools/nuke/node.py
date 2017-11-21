import os

import nuke


def create(node_class):
    nuke.nodePaste(os.path.join(os.path.dirname(__file__), node_class + ".nk"))
