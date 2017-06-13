import os

from conda_git_deployment import utils


root = os.path.dirname(__file__)
environment = {}

# PYTHONPATH
environment["PYTHONPATH"] = [os.path.join(root, "environment", "PYTHONPATH")]

# NUKE_PATH
environment["NUKE_PATH"] = [os.path.join(root, "environment", "NUKE_PATH")]

# HOUDINI_PATH
# NOTE: Houdini's env file in the users directory, does not like backslashes
environment["HOUDINI_PATH"] = [
    os.path.join(root, "environment", "HOUDINI_PATH").replace("\\", "/"), "&"
]

# HIERO_PLUGIN_PATH
environment["HIERO_PLUGIN_PATH"] = [
    os.path.join(root, "environment", "HIERO_PLUGIN_PATH")
]

utils.write_environment(environment)
