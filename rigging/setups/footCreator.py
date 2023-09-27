# ------------------------------------------------------------------------------------------
#
# --------------------  Auto Foot Script v1.0 by Elio Molinaro  -------------------------
#
# ------------------------------------------------------------------------------------------

"""Auto foot setup based on basic foot joints and a curve around the geo of the foot"""

import maya.cmds as cmds
import maya.mel as mm
from math import sqrt


# Get the distance between two shapes
def getDistance(first, second):

    matrix_first = cmds.xform(first, q=True, t=True, ws=True)
    matrix_second = cmds.xform(second, q=True, t=True, ws=True)

    return sqrt(pow(matrix_first[0] - matrix_second[0], 2) + pow(matrix_first[1] - matrix_second[1], 2) + pow(
        matrix_first[2] - matrix_second[2], 2))


# Change colour of the controllers
def changeColour(controller, colour):

    controller_shape = cmds.listRelatives(controller, shapes=1)

    if controller_shape is None:
        pass
    else:
        for i in controller_shape:
            cmds.setAttr(i + '.overrideEnabled', 1)
            cmds.setAttr(i + '.overrideColor', colour)


# Create matrix constraint function
def matrixConstraint(child, parent, type, maintain_offset):
    # Get child parent
    child_parent = cmds.listRelatives(child, p=True)
    child_parent = child_parent[0]

    if maintain_offset is True:
        proxy_attr = cmds.addAttr(parent, sn='proxyAttr', dt='matrix')

    # create nodes
    if maintain_offset is True:
        mult_matrix_maintain = cmds.createNode('multMatrix', n=f'{objects_name}_maintain_mm')

    mult_matrix = cmds.createNode('multMatrix', n=f'{objects_name}_mm')
    decompose_matrix = cmds.createNode('decomposeMatrix', n=f'{objects_name}_dcm')

    # Make connections
    if maintain_offset is True:
        cmds.connectAttr(f'{child}.worldMatrix[0]', f'{mult_matrix_maintain}.matrixIn[0]')
        cmds.connectAttr(f'{parent}.worldInverseMatrix[0]', f'{mult_matrix_maintain}.matrixIn[1]')
        cmds.connectAttr(f'{mult_matrix_maintain}.matrixSum', f'{parent}.proxyAttr')
        cmds.disconnectAttr(f'{mult_matrix_maintain}.matrixSum', f'{parent}.proxyAttr')
        cmds.connectAttr(f'{parent}.proxyAttr', f'{mult_matrix}.matrixIn[0]')
        cmds.connectAttr(f'{parent}.worldMatrix[0]', f'{mult_matrix}.matrixIn[1]')
        cmds.connectAttr(f'{child_parent}.worldInverseMatrix[0]', f'{mult_matrix}.matrixIn[2]')
        cmds.connectAttr(f'{mult_matrix}.matrixSum', f'{decompose_matrix}.inputMatrix')
        cmds.delete(mult_matrix_maintain)
    elif maintain_offset is False:
        cmds.connectAttr(f'{parent}.worldMatrix[0]', f'{mult_matrix}.matrixIn[0]')
        cmds.connectAttr(f'{child_parent}.worldInverseMatrix[0]', f'{mult_matrix}.matrixIn[1]')
        cmds.connectAttr(f'{mult_matrix}.matrixSum', f'{decompose_matrix}.inputMatrix')

    if type == 'parent':
        cmds.connectAttr(f'{decompose_matrix}.outputTranslate', f'{child}.translate')
        cmds.connectAttr(f'{decompose_matrix}.outputRotate', f'{child}.rotate')
        cmds.connectAttr(f'{decompose_matrix}.outputScale', f'{child}.scale')

    elif type == 'point':
        cmds.connectAttr(f'{decompose_matrix}.outputTranslate', f'{child}.translate')

    elif type == 'orient':
        cmds.connectAttr(f'{decompose_matrix}.outputRotate', f'{child}.rotate')

    if cmds.nodeType(child) == 'joint':
        cmds.setAttr(f'{child}.jointOrientX', 0)
        cmds.setAttr(f'{child}.jointOrientY', 0)
        cmds.setAttr(f'{child}.jointOrientZ', 0)


# Create function to hide unwanted Renderman attributes
def rmanAttrsHide(controller):
    cmds.setAttr(f'{controller}.rman_matteObject', lock=1, keyable=0, channelBox=0)
    cmds.setAttr(f'{controller}.rman_holdout', lock=1, keyable=0, channelBox=0)
    cmds.setAttr(f'{controller}.rman_nestedInstancing', lock=1, keyable=0, channelBox=0)
    cmds.setAttr(f'{controller}.rman_maxDiffuseDepth', lock=1, keyable=0, channelBox=0)
    cmds.setAttr(f'{controller}.rman_maxSpecularDepth', lock=1, keyable=0, channelBox=0)
    cmds.setAttr(f'{controller}.rman_relativePixelVariance', lock=1, keyable=0, channelBox=0)
    cmds.setAttr(f'{controller}.rman_intersectPriority', lock=1, keyable=0, channelBox=0)
    cmds.setAttr(f'{controller}.rman_visibilityCamera', lock=1, keyable=0, channelBox=0)
    cmds.setAttr(f'{controller}.rman_visibilityIndirect', lock=1, keyable=0, channelBox=0)
    cmds.setAttr(f'{controller}.rman_visibilityTransmission', lock=1, keyable=0, channelBox=0)
    cmds.setAttr(f'{controller}.rman_motionSamples', lock=1, keyable=0, channelBox=0)
    cmds.setAttr(f'{controller}.rman_renderCurve', lock=1, keyable=0, channelBox=0)
    cmds.setAttr(f'{controller}.rman_curveBaseWidth', lock=1, keyable=0, channelBox=0)
    cmds.setAttr(f'{controller}.rman_curveTipWidth', lock=1, keyable=0, channelBox=0)


# Treat the user input use it to create a secondary curve
def inputObjects():

    global target_crv
    global  dest_crv

    # Pre-process the curve
    dest_crv = cmds.ls(sl=1)[0]
    dest_crv = cmds.rename(dest_crv, f'crv_{objects_name}_dest')
    mm.eval('CenterPivot;')
    cmds.makeIdentity(dest_crv, a=1)
    cmds.delete(ch=1)

    # Create the target curve and rebuild both to 12 points
    cmds.rebuildCurve(dest_crv, s=12, end=1, kr=2, kep=0, kt=0, ch=0)

    radius_target = getDistance(f'{dest_crv}.cv[3]', f'{dest_crv}.cv[9]') / 2.25 / 2

    target_crv = cmds.circle(nr=[0, 1, 0], r=radius_target, n=f'crv_{objects_name}_target', ch=0)[0]
    cmds.matchTransform(target_crv, dest_crv)
    cmds.setAttr(f'{target_crv}.rotateZ', 180)
    cmds.setAttr(f'{target_crv}.rotateY', 30)
    cmds.makeIdentity(target_crv, a=1)
    cmds.rebuildCurve(target_crv, s=12, end=1, kr=2, kep=0, kt=0, ch=0)


# Create the controllers and locators used for the setup
def createControllers():

    global target_crv
    global dest_crv
    global target_loc
    global dest_loc
    global foot_ctrl

    # Create controllers
    foot_ctrl = mm.eval('curve -d 1 -p -0.5214 0 0.5214 -p -1.056 0 0.363 -p -0.99 0 0.66 -p -1.65 0 0 -p -0.99 0 -0.66 -p -1.056 0 -0.363 -p -0.5214 0 -0.5214 -p -0.363 0 -1.056 -p -0.66 0 -0.99 -p 0 0 -1.65 -p 0.66 0 -0.99 -p 0.363 0 -1.056 -p 0.5214 0 -0.5214 -p 1.056 0 -0.363 -p 0.99 0 -0.66 -p 1.65 0 0 -p 0.99 0 0.66 -p 1.056 0 0.363 -p 0.5214 0 0.5214 -p 0.363 0 1.056 -p 0.66 0 0.99 -p 0 0 1.65 -p -0.66 0 0.99 -p -0.363 0 1.056 -p -0.5214 0 0.5214 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 -k 18 -k 19 -k 20 -k 21 -k 22 -k 23 -k 24 ;')
    foot_ctrl = cmds.rename(foot_ctrl, f'ctrl_{objects_name}_foot')
    foot_offset = cmds.group(foot_ctrl, n=f'offset_{objects_name}_foot')
    cmds.matchTransform(foot_offset, target_crv)

    ctrl_scale = getDistance(f'{dest_crv}.cv[0]', f'{dest_crv}.cv[6]') / 2.5
    cmds.setAttr(f'{foot_ctrl}.scaleX', ctrl_scale)
    cmds.setAttr(f'{foot_ctrl}.scaleY', ctrl_scale)
    cmds.setAttr(f'{foot_ctrl}.scaleZ', ctrl_scale)
    cmds.makeIdentity(foot_ctrl, a=1)

    ctrl_scale = getDistance(f'{dest_crv}.cv[0]', f'{dest_crv}.cv[6]') / 2
    foot_roll_ctrl = cmds.circle(nr=[0, 1, 0], r=ctrl_scale, n=f'ctrl_{objects_name}_footRoll', ch=0)[0]
    foot_roll_offset = cmds.group(foot_roll_ctrl, n=f'offset_{objects_name}_footRoll')
    cmds.matchTransform(foot_roll_offset, target_crv)

    cmds.delete(foot_roll_ctrl, foot_ctrl, ch=1)

    # Create locators
    target_loc = cmds.spaceLocator(n=f'loc_{objects_name}_target')[0]
    dest_loc = cmds.spaceLocator(n=f'loc_{objects_name}_dest')[0]
    cmds.matchTransform(target_loc, target_crv)
    cmds.parent(target_loc, foot_roll_ctrl)

    # Create the parenting chain
    cmds.parent(foot_roll_offset, target_crv, dest_crv, dest_loc, foot_ctrl)
    cmds.select(cl=1)

    # Cosmetic changes
    rmanAttrsHide(foot_ctrl)
    rmanAttrsHide(foot_roll_ctrl)
    changeColour(foot_ctrl, 13)
    changeColour(foot_roll_ctrl, 17)
    #cmds.hide(dest_loc, dest_crv, target_loc, target_crv)


# Create the angle detection system with the curves
def curveConform():

    # Create nodes
    decomp_matrix_01 = cmds.createNode('decomposeMatrix', n=f'{objects_name}_crv_conform_dm')
    nearest_poc = cmds.createNode('nearestPointOnCurve', n=f'{objects_name}_crv_conform_nearpoc')
    poc_info = cmds.createNode('pointOnCurveInfo', n=f'{objects_name}_crv_conform_poc')

    decomp_matrix_02 = cmds.createNode('decomposeMatrix', n=f'{objects_name}_loc_norm_dm')
    comp_matrix = cmds.createNode('composeMatrix', n=f'{objects_name}_loc_norm_cm')
    mult_matrix = cmds.createNode('multMatrix', n=f'{objects_name}_loc_norm_mm')

    # Get needed shapes
    target_crv_shape = cmds.listRelatives(target_crv, s=1)[0]
    dest_crv_shape = cmds.listRelatives(dest_crv, s=1)[0]

    # Create connexions
    cmds.connectAttr(f'{target_loc}.worldMatrix', f'{decomp_matrix_01}.inputMatrix')
    cmds.connectAttr(f'{decomp_matrix_01}.outputTranslate', f'{nearest_poc}.inPosition')
    cmds.connectAttr(f'{target_crv_shape}.worldSpace', f'{nearest_poc}.inputCurve')
    cmds.connectAttr(f'{nearest_poc}.parameter', f'{poc_info}.parameter')
    cmds.connectAttr(f'{dest_crv_shape}.worldSpace', f'{poc_info}.inputCurve')
    cmds.connectAttr(f'{poc_info}.position', f'{comp_matrix}.inputTranslate')
    cmds.connectAttr(f'{comp_matrix}.outputMatrix', f'{mult_matrix}.matrixIn[0]')
    cmds.connectAttr(f'{foot_ctrl}.worldInverseMatrix', f'{mult_matrix}.matrixIn[1]')
    cmds.connectAttr(f'{mult_matrix}.matrixSum', f'{decomp_matrix_02}.inputMatrix')
    cmds.connectAttr(f'{decomp_matrix_02}.outputTranslate', f'{dest_loc}.translate')


# Run the script
def runScript(*args):

    inputObjects()
    createControllers()
    curveConform()

    cmds.select(cl=1)


# Create the UI
def autoFootUI():

    global objects_name

    result = cmds.promptDialog(
        title='Auto Foot Tool v1.0',
        message='Foot Name:',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel')

    if result == 'OK':
        if len(cmds.promptDialog(query=True, text=True)) == 0:
            objects_name = 'tempFoot'
        else:
            objects_name = cmds.promptDialog(query=True, text=True)

        runScript()


autoFootUI()
