import os
import re
import webbrowser
import subprocess
import math

import nuke


def open_from_node():
    for node in nuke.selectedNodes():
        path = nuke.filename(node)

        if path is None:
            continue

        path = os.path.dirname(path)

        if not os.path.exists(path):
            os.makedirs(path)

        webbrowser.open("file://{0}".format(path))


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


def createExrCamVray(node):
    '''
    Create a camera node based on VRay metadata.
    This works specifically on VRay data coming from maya.

    From https://pastebin.com/4vmAmARU
    '''

    # Big thanks to Ivan Busquets who helped me put this together!
    # (ok, ok, he really helped me a lot)
    # Also thanks to Nathan Dunsworth for giving me solid ideas and some code
    # to get me started.

    # TODO : add progress bar (even though it's really not needed here) that
    # works

    mDat = node.metadata()
    reqFields = [
        'exr/camera%s' % i for i in ('FocalLength', 'Aperture', 'Transform')
    ]
    if not set(reqFields).issubset(mDat):
        print 'no metdata for camera found'
        return

    first = node.firstFrame()
    last = node.lastFrame()
    ret = nuke.getFramesAndViews(
        'Create Camera from Metadata', '%s-%s' % (first, last)
    )
    fRange = nuke.FrameRange(ret[0])

    cam = nuke.createNode('Camera2')
    cam['useMatrix'].setValue(False)

    for k in ('focal', 'haperture', 'translate', 'rotate'):
        cam[k].setAnimated()

    for curTask, frame in enumerate(fRange):
        # IB. If you get both focal and aperture as they are in the metadata,
        # there's no guarantee
        # your Nuke camera will have the same FOV as the one that rendered the
        # scene (because the render could have been fit to horizontal, to
        # vertical, etc)
        # Nuke always fits to the horizontal aperture. If you set the
        # horizontal aperture as it is in the metadata,
        # then you should use the FOV in the metadata to figure out the
        # correct focal length for Nuke's camera
        # Or, you could keep the focal as is in the metadata, and change the
        # horizontal_aperture instead.
        # I'll go with the former here. Set the haperture knob as per the
        # metadata, and derive the focal length from the FOV

        # get horizontal aperture
        val = node.metadata('exr/cameraAperture', frame)
        # get camera FOV
        fov = node.metadata('exr/cameraFov', frame)

        # convert the fov and aperture into focal length
        focal = val / (2 * math.tan(math.radians(fov)/2.0))

        cam['focal'].setValueAt(float(focal), frame)
        cam['haperture'].setValueAt(float(val), frame)

        # get camera transform data
        matrixCamera = node.metadata('exr/cameraTransform', frame)

        # Create a matrix to shove the original data into
        matrixCreated = nuke.math.Matrix4()

        for k, v in enumerate(matrixCamera):
            matrixCreated[k] = v

        # this is needed for VRay.  It's a counter clockwise rotation
        matrixCreated.rotateX(math.radians(-90))
        # Get a vector that represents the camera translation
        translate = matrixCreated.transform(nuke.math.Vector3(0, 0, 0))
        # give us xyz rotations from cam matrix (must be converted to degrees)
        rotate = matrixCreated.rotationsZXY()

        cam['translate'].setValueAt(float(translate.x), frame, 0)
        cam['translate'].setValueAt(float(translate.y), frame, 1)
        cam['translate'].setValueAt(float(translate.z), frame, 2)
        cam['rotate'].setValueAt(float(math.degrees(rotate[0])), frame, 0)
        cam['rotate'].setValueAt(float(math.degrees(rotate[1])), frame, 1)
        cam['rotate'].setValueAt(float(math.degrees(rotate[2])), frame, 2)
