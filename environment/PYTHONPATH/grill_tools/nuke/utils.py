import os
import re
import webbrowser
import subprocess

import nuke


def open_from_node():
    for node in nuke.selectedNodes():
        path = nuke.filename(node)

        if path is None:
            continue

        webbrowser.open("file://{0}".format(os.path.dirname(path)))


def get_regex_files(pattern_items):
    """Traverse the pattern items to find files with regex expressions.

    Usage:
        >>> pattern_items = [
                "C:" + os.sep,
                "Program Files",
                "djv-[0-9].[0-9].[0-9]-Windows-64",
                "bin",
                "djv_view.exe"
            ]
        >>> get_regex_files(pattern_items)
        [
            "C:\\Program Files\\djv-1.1.0-Windows-64\\bin\\djv_view.exe",
            "C:\\Program Files\\djv-1.0.0-Windows-64\\bin\\djv_view.exe"
        ]
    """

    # Construct patterns from pattern items
    patterns = []
    pattern = ""
    for item in pattern_items:
        pattern = os.path.join(pattern, item)
        patterns.append("^{0}$".format(pattern.replace("\\", "\\\\")))

    # Find files from patterns
    files = []
    for root, dirnames, filenames in os.walk(pattern_items[0], topdown=True):

        # Remove invalid directories to search
        for i in reversed(range(len(dirnames))):
            path = os.path.join(root, dirnames[i])
            valid_path = False
            for pattern in patterns:
                if re.match(pattern, path):
                    valid_path = True
            if not valid_path:
                del dirnames[i]

        # Collect all valid file paths
        for f in filenames:
            path = os.path.join(root, f)
            for pattern in patterns:
                if re.match(pattern, path):
                    files.append(path)

    return files


def open_with_djv():
    pattern_items = [
        "C:" + os.sep,
        "Program Files",
        "djv-[0-9].[0-9].[0-9]-Windows-64",
        "bin",
        "djv_view.exe"
    ]
    executables = get_regex_files(pattern_items)
    args = [executables[0], nuke.filename(nuke.selectedNode(), nuke.REPLACE)]
    subprocess.Popen(args)
