import imp
import os

import pymel.core as pm
import maya.cmds as mc
import maya.mel as mm

import pyblish.api


# Quiet load alembic plugins
pm.loadPlugin("AbcExport.mll", quiet=True)
pm.loadPlugin("AbcImport.mll", quiet=True)


# Set project to workspace next to scene file.
def grill_tools_set_workspace():
    work_dir = os.path.dirname(os.path.abspath(pm.system.sceneName()))
    workspace = os.path.join(work_dir, "workspace")

    if not os.path.exists(workspace):
        os.makedirs(workspace)

    pm.system.Workspace.open(work_dir)

    rules = [
        "3dPaintTextures",
        "ASS",
        "ASS Export",
        "Alembic",
        "BIF",
        "CATIAV4_ATF",
        "CATIAV5_ATF",
        "DAE_FBX",
        "DAE_FBX export",
        "Fbx",
        "IGES_ATF",
        "INVENTOR_ATF",
        "JT_ATF",
        "NX_ATF",
        "OBJ",
        "OBJexport",
        "PROE_ATF",
        "SAT_ATF",
        "STEP_ATF",
        "STL_ATF",
        "alembicCache",
        "audio",
        "autoSave",
        "bifrostCache",
        "clips",
        "depth",
        "diskCache",
        "eps",
        "fileCache",
        "fluidCache",
        "furAttrMap",
        "furEqualMap",
        "furFiles",
        "furImages",
        "furShadowMap",
        "illustrator",
        "images",
        "iprImages",
        "mayaAscii",
        "mayaBinary",
        "mel",
        "move",
        "movie",
        "offlineEdit",
        "particles",
        "renderData",
        "sceneAssembly",
        "scripts",
        "shaders",
        "sound",
        "sourceImages",
        "teClipExports",
        "templates",
        "timeEditor",
        "translatorData"
    ]

    for item in rules:
        pm.Workspace.fileRules[item] = "workspace"

    # Scene is needs to be directly in the project folder,
    # so people can open old versions and save as new versions.
    pm.Workspace.fileRules["scene"] = ""

    pm.system.Workspace.save()


if os.environ.get("GRILL_TOOLS_SET_WORKSPACE", ""):
    pm.evalDeferred("grill_tools_set_workspace()")

# Setup for pyblish
mc.evalDeferred("from grill_tools.maya import pyblish_init;pyblish_init.init()")


# Adding grill-tools menu
def grill_tools_menu_init():

    gMainWindow = mm.eval("$temp1=$gMainWindow")
    if mc.menu("grill-tools", exists=True):
        mc.deleteUI("grill-tools")

    menu = mc.menu(
        "grill-tools",
        parent=gMainWindow,
        tearOff=False,
        label="grill-tools"
    )

    mc.menuItem(
        "processingLocation",
        label="Processing Location",
        parent=menu,
        command=(
            "from grill_tools.maya import processing_location;" +
            "processing_location.show()"
        )
    )


mc.evalDeferred("grill_tools_menu_init()")

# Adding ftrack assets if import is available.
try:
    imp.find_module("ftrack_connect")
    imp.find_module("ftrack_connect_maya")

    from grill_tools.maya import ftrack_assets
    ftrack_assets.register_assets()
    from grill_tools.maya import ftrack_init
    ftrack_init.init()
except ImportError as error:
    print "Could not find ftrack modules: " + str(error)
