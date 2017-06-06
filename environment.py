import os

from conda_git_deployment import utils


root = os.path.dirname(__file__)
environment = {}

# PYTHONPATH
environment["PYTHONPATH"] = [os.path.join(root, "environment", "PYTHONPATH")]

# NUKE_PATH
environment["NUKE_PATH"] = [os.path.join(root, "environment", "NUKE_PATH")]

# HOUDINI_PATH
environment["HOUDINI_PATH"] = [
    os.path.join(root, "environment", "HOUDINI_PATH"), "&"
]

# HIERO_PLUGIN_PATH
environment["HIERO_PLUGIN_PATH"] = [
    os.path.join(root, "environment", "HIERO_PLUGIN_PATH")
]

utils.write_environment(environment)
