import sys
import subprocess
import tempfile
import os
import shutil

import nuke


def create():
    script = __file__
    directory_name = tempfile.mkdtemp()
    clipboard_path = os.path.join(directory_name, "clipboard.nk")

    # First try with a render license
    p = subprocess.Popen(
        [
            sys.executable,
            "-t",
            script,
            clipboard_path,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    communicate = p.communicate()

    # Second try an interactive license
    if p.returncode != 0:
        p = subprocess.Popen(
            [
                sys.executable,
                "-i",
                "-t",
                script,
                clipboard_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        communicate = p.communicate()

    # Raise error if both licenses fail
    if p.returncode != 0:
        raise ValueError(communicate[0])

    nuke.nodePaste(clipboard_path)

    shutil.rmtree(directory_name)


def main():
    node = nuke.createNode("Write")

    # File output path
    file_path = (
        "[python {nuke.script_directory()}]/workspace/[python "
        "{nuke.thisNode().name()}]/[python {os.path.splitext("
        "os.path.basename(nuke.scriptName()))[0]}]/[python {"
        "os.path.splitext(os.path.basename(nuke.scriptName()))[0]}]_"
        "[python {nuke.thisNode().name()}].%04d.exr"
    )
    node["file"].setValue(file_path)

    # Setting the file type
    node["file_type"].setValue("exr")

    # Setting metadata
    node["metadata"].setValue("all metadata")

    # Setting autocrop
    node["autocrop"].setValue(True)

    # Enable create directories if it exists.
    # Older version of Nuke does not have this option.
    if "create_directories" in node.knobs():
        node["create_directories"].setValue(True)

    for node in nuke.allNodes():
        node["selected"].setValue(True)

    clipboard_path = sys.argv[1].replace("\\", "/")
    nuke.nodeCopy(clipboard_path)


if __name__ == "__main__":
    main()
