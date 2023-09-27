# ------------------------------------------------------------------------------------------
#
# --------------------  IK FK Limb Script v1.5 by Elio Molinaro  -------------------------
#
# ------------------------------------------------------------------------------------------

"""Limb Creator based on a joint selection"""

import maya.cmds as cmds
import pymel.core as pm
from math import pow, sqrt


# Setting Constants
GREY = 3
BLACK = 1
BLUE = 6
MAGENTA = 9
RED = 13
GREEN = 14
WHITE = 15
YELLOW = 17
CYAN = 18


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
        mult_matrix_maintain = cmds.createNode('multMatrix', n=f'{joints_name}_maintain_mm')

    mult_matrix = cmds.createNode('multMatrix', n=f'{joints_name}_mm')
    decompose_matrix = cmds.createNode('decomposeMatrix', n=f'{joints_name}_dcm')

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


# Get user's selection, verify if it's correct, and process it
def userSel():
    global sk_jnts

    sel = cmds.ls(sl=1)

    if len(sel) == 1:
        sk_jnt_01 = sel[0]
        sk_jnt_02 = cmds.listRelatives(sk_jnt_01, children=1)[0]
        sk_jnt_03 = cmds.listRelatives(sk_jnt_02, children=1)[0]

        sk_jnt_01 = cmds.rename(sk_jnt_01, f'sk_{joints_name}_01')
        sk_jnt_02 = cmds.rename(sk_jnt_02, f'sk_{joints_name}_02')
        sk_jnt_03 = cmds.rename(sk_jnt_03, f'sk_{joints_name}_03')

        if cmds.nodeType(sk_jnt_01) != 'joint' or cmds.nodeType(sk_jnt_02) != 'joint' or cmds.nodeType(
                sk_jnt_03) != 'joint':
            cmds.error('Please only select one joint that has 2 children joints')
        else:
            sk_jnts = [sk_jnt_01, sk_jnt_02, sk_jnt_03]

    else:
        cmds.error('Please only select one joint that has 2 children joints')

    if cmds.objExists('grp_JNTS') is True:
        if sk_jnt_01 in cmds.listRelatives('grp_JNTS', c=1):
            pass
        else:
            cmds.parent(sk_jnt_01, 'grp_JNTS')
    else:
        cmds.group(empty=1, name='grp_JNTS')
        cmds.parent(sk_jnt_01, 'grp_JNTS')

    cmds.hide(sk_jnts)


# Create the ik and fk joints, their controllers, and their constraints
def createJointsControllers():
    global ik_jnts
    global fk_jnts
    global switch_control
    global switch_offset
    global ik_wrist_control
    global ik_wrist_offset
    global ik_shoulder_control
    global ik_shoulder_offset
    global pv_control
    global fk_ctrls

    # Create IK joints
    ik_jnt_01 = cmds.duplicate(sk_jnts[0], n=f'ik_{joints_name}_01', po=1)[0]
    ik_jnt_02 = cmds.duplicate(sk_jnts[1], n=f'ik_{joints_name}_01', po=1)[0]
    ik_jnt_03 = cmds.duplicate(sk_jnts[2], n=f'ik_{joints_name}_01', po=1)[0]

    ik_jnts = [ik_jnt_01, ik_jnt_02, ik_jnt_03]
    cmds.hide(ik_jnt_01)

    cmds.parent(ik_jnt_03, ik_jnt_02)
    cmds.parent(ik_jnt_02, ik_jnt_01)

    # Create FK joints
    fk_jnt_01 = cmds.duplicate(sk_jnts[0], n=f'fk_{joints_name}_01', po=1)[0]
    fk_jnt_02 = cmds.duplicate(sk_jnts[1], n=f'fk_{joints_name}_01', po=1)[0]
    fk_jnt_03 = cmds.duplicate(sk_jnts[2], n=f'fk_{joints_name}_01', po=1)[0]

    fk_jnts = [fk_jnt_01, fk_jnt_02, fk_jnt_03]
    cmds.hide(fk_jnt_01)

    cmds.parent(fk_jnt_03, fk_jnt_02)
    cmds.parent(fk_jnt_02, fk_jnt_01)

    # Create the IK wrist controller
    ik_wrist_control = pm.language.Mel.eval(
        'curve -d 1 -p 1 1 1 -p -1 1 1 -p -1 1 -1 -p 1 1 -1 -p 1 1 1 -p 1 -1 1 -p 1 -1 -1 -p 1 1 -1 -p -1 1 -1 -p -1 -1 -1 -p -1 -1 1 -p -1 1 1 -p -1 -1 1 -p 1 -1 1 -p 1 -1 -1 -p -1 -1 -1 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 ;')
    ik_wrist_control = cmds.rename(ik_wrist_control, f'ctrl_ik_{joints_name}_02')
    ik_wrist_offset = cmds.group(ik_wrist_control, n=f'offset_ik_{joints_name}_02')
    cmds.setAttr(f'{ik_wrist_control}.scaleX', 4.5)
    cmds.setAttr(f'{ik_wrist_control}.scaleY', 4.5)
    cmds.setAttr(f'{ik_wrist_control}.scaleZ', 4.5)
    cmds.makeIdentity(ik_wrist_control, a=1)
    cmds.matchTransform(ik_wrist_offset, ik_jnt_03)
    rmanAttrsHide(ik_wrist_control)
    changeColour(ik_wrist_control, CYAN)

    # Create the IK shoulder controller
    ik_shoulder_control = pm.language.Mel.eval(
        'curve -d 1 -p 1 1 1 -p -1 1 1 -p -1 1 -1 -p 1 1 -1 -p 1 1 1 -p 1 -1 1 -p 1 -1 -1 -p 1 1 -1 -p -1 1 -1 -p -1 -1 -1 -p -1 -1 1 -p -1 1 1 -p -1 -1 1 -p 1 -1 1 -p 1 -1 -1 -p -1 -1 -1 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 ;')
    ik_shoulder_control = cmds.rename(ik_shoulder_control, f'ctrl_ik_{joints_name}_01')
    ik_shoulder_offset = cmds.group(ik_shoulder_control, n=f'offset_ik_{joints_name}_01')
    cmds.setAttr(f'{ik_shoulder_control}.scaleX', 5.5)
    cmds.setAttr(f'{ik_shoulder_control}.scaleY', 5.5)
    cmds.setAttr(f'{ik_shoulder_control}.scaleZ', 5.5)
    cmds.makeIdentity(ik_shoulder_control, a=1)
    cmds.matchTransform(ik_shoulder_offset, ik_jnt_01)
    rmanAttrsHide(ik_shoulder_control)
    changeColour(ik_shoulder_control, CYAN)

    # Create the pole vector controller
    pv_control = pm.language.Mel.eval(
        'curve -d 1 -p 0.622376 -0.656174 0.622376 -p 0.622376 -0.656174 -0.622376 -p -0.622376 -0.656174 -0.622376 -p -0.622376 -0.656174 0.622376 -p 0.622376 -0.656174 0.622376 -p 0 1.112776 0 -p -0.622376 -0.656174 0.622376 -p -0.622376 -0.656174 -0.622376 -p 0 1.112776 0 -p 0.622376 -0.656174 -0.622376 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 ;')
    pv_control = cmds.rename(pv_control, f'ctrl_pv_{joints_name}')
    cmds.setAttr(f'{pv_control}.scaleX', 4)
    cmds.setAttr(f'{pv_control}.scaleY', 4)
    cmds.setAttr(f'{pv_control}.scaleZ', 4)
    cmds.makeIdentity(pv_control, a=1)
    cmds.move(0, 0, 0, f"{pv_control}.scalePivot", f"{pv_control}.rotatePivot", absolute=True)
    pv_offset = cmds.group(em=1, n=f'offset_pv_{joints_name}')
    cmds.parent(pv_control, pv_offset)
    cmds.matchTransform(pv_offset, ik_jnt_02, pos=1)
    rmanAttrsHide(pv_control)
    changeColour(pv_control, CYAN)


    # Create the FK controllers
    fk_01_control = cmds.circle(name=f'ctrl_fk_{joints_name}_01', normal=[1, 0, 0], r=7)[0]
    cmds.delete(fk_01_control, ch=1)
    fk_01_offset = cmds.group(fk_01_control, n=f'offset_fk_{joints_name}_01')
    cmds.matchTransform(fk_01_offset, fk_jnt_01)
    rmanAttrsHide(fk_01_control)
    changeColour(fk_01_control, RED)

    fk_02_control = cmds.circle(name=f'ctrl_fk_{joints_name}_02', normal=[1, 0, 0], r=7)[0]
    cmds.delete(fk_02_control, ch=1)
    fk_02_offset = cmds.group(fk_02_control, n=f'offset_fk_{joints_name}_02')
    cmds.matchTransform(fk_02_offset, fk_jnt_02)
    rmanAttrsHide(fk_02_control)
    changeColour(fk_02_control, RED)

    fk_03_control = cmds.circle(name=f'ctrl_fk_{joints_name}_03', normal=[1, 0, 0], r=7)[0]
    cmds.delete(fk_03_control, ch=1)
    fk_03_offset = cmds.group(fk_03_control, n=f'offset_fk_{joints_name}_03')
    cmds.matchTransform(fk_03_offset, fk_jnt_03)
    rmanAttrsHide(fk_03_control)
    changeColour(fk_03_control, RED)

    cmds.parent(fk_03_offset, fk_02_control, a=1)
    cmds.parent(fk_02_offset, fk_01_control, a=1)

    fk_ctrls = [fk_01_control, fk_02_control, fk_03_control]

    # Create the switch controller
    switch_control = pm.language.Mel.eval(
        'curve -d 1 -p -0.414 0 0.414 -p -1.242 0 0.414 -p -1.242 0 -0.414 -p -0.414 0 -0.414 -p -0.414 0 -1.242 -p 0.414 0 -1.242 -p 0.414 0 -0.414 -p 1.242 0 -0.414 -p 1.242 0 0.414 -p 0.414 0 0.414 -p 0.414 0 1.242 -p -0.414 0 1.242 -p -0.414 0 0.414 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 ;')
    cmds.setAttr(f'{switch_control}.scaleX', 2)
    cmds.setAttr(f'{switch_control}.scaleY', 2)
    cmds.setAttr(f'{switch_control}.scaleZ', 2)
    cmds.setAttr(f'{switch_control}.rotateX', 90)
    cmds.makeIdentity(switch_control, a=1)
    switch_control = cmds.rename(switch_control, f'ctrl_switch_{joints_name}')
    switch_constrain = cmds.group(switch_control, n=f'constrain_switch_{joints_name}')
    switch_offset = cmds.group(switch_constrain, n=f'offset_switch_{joints_name}')
    cmds.matchTransform(switch_offset, sk_jnts[2], pos=1)
    cmds.addAttr(switch_control, at='double', nn='IK FK Switch', sn='ikFkSwitch', min=0, max=10, dv=0, keyable=1)
    rmanAttrsHide(switch_control)
    changeColour(switch_control, YELLOW)

    # Check if CTRLS group exists and parent to it or create it
    if cmds.objExists('grp_CTRLS') is True:
        cmds.parent(ik_wrist_offset, 'grp_CTRLS')
        cmds.parent(ik_shoulder_offset, 'grp_CTRLS')
        cmds.parent(pv_offset, 'grp_CTRLS')
        cmds.parent(switch_offset, 'grp_CTRLS')
        cmds.parent(fk_01_offset, 'grp_CTRLS')
    else:
        cmds.group(empty=1, name='grp_CTRLS')
        cmds.parent(ik_wrist_offset, 'grp_CTRLS')
        cmds.parent(ik_shoulder_offset, 'grp_CTRLS')
        cmds.parent(pv_offset, 'grp_CTRLS')
        cmds.parent(switch_offset, 'grp_CTRLS')
        cmds.parent(fk_01_offset, 'grp_CTRLS')

    # Create the IK handle
    ik_handle = cmds.ikHandle(sj=ik_jnt_01, ee=ik_jnt_03, n=f'ikrp_{joints_name}_handle')[0]
    cmds.parent(ik_handle, ik_wrist_control)
    cmds.hide(ik_handle)

    # Create the joints constraints
    matrixConstraint(fk_jnt_01, fk_01_control, 'parent', False)
    matrixConstraint(fk_jnt_02, fk_02_control, 'parent', False)
    matrixConstraint(fk_jnt_03, fk_03_control, 'parent', False)
    matrixConstraint(ik_jnt_01, ik_shoulder_control, 'point', False)
    matrixConstraint(ik_jnt_03, ik_wrist_control, 'orient', False)

    # Create the PV constrain
    cmds.poleVectorConstraint(pv_control, ik_handle)


# Create blending between FK and IK
def blendingSwitch():
    global value_X_up
    global value_X_lo

    md_node = cmds.createNode('multiplyDivide', n=f'{joints_name}_switch_mm')
    reverse_node = cmds.createNode('reverse', n=f'{joints_name}_switch_rv')
    cmds.connectAttr(f'{switch_control}.ikFkSwitch', f'{md_node}.input1.input1X')
    cmds.connectAttr(f'{switch_control}.ikFkSwitch', f'{ik_wrist_control}.visibility')
    cmds.connectAttr(f'{switch_control}.ikFkSwitch', f'{ik_shoulder_control}.visibility')
    cmds.connectAttr(f'{switch_control}.ikFkSwitch', f'{pv_control}.visibility')
    cmds.connectAttr(f'{md_node}.outputX', f'{reverse_node}.inputX')
    cmds.setAttr(f'{md_node}.input2X', 10)
    cmds.setAttr(f'{md_node}.operation', 2)

    value_X_up = cmds.getAttr(f'{ik_jnts[1]}.translateX')
    value_X_lo = cmds.getAttr(f'{ik_jnts[2]}.translateX')

    for i in range(3):
        blend_matrix = cmds.createNode('blendMatrix', n=f'{joints_name}_switch{i+1}_blm')
        cmds.connectAttr(f'{fk_jnts[i]}.worldMatrix[0]', f'{blend_matrix}.inputMatrix')
        cmds.connectAttr(f'{ik_jnts[i]}.worldMatrix[0]', f'{blend_matrix}.target[0].targetMatrix')
        cmds.connectAttr(f'{blend_matrix}.outputMatrix', f'{sk_jnts[i]}.offsetParentMatrix')
        cmds.setAttr(f'{sk_jnts[i]}.translateX', 0)
        cmds.setAttr(f'{sk_jnts[i]}.translateY', 0)
        cmds.setAttr(f'{sk_jnts[i]}.translateZ', 0)
        cmds.setAttr(f'{sk_jnts[i]}.jointOrientX', 0)
        cmds.setAttr(f'{sk_jnts[i]}.jointOrientY', 0)
        cmds.setAttr(f'{sk_jnts[i]}.jointOrientZ', 0)
        cmds.setAttr(f'{sk_jnts[i]}.inheritsTransform', 0)
        cmds.connectAttr(f'{md_node}.outputX', f'{blend_matrix}. envelope')
        cmds.connectAttr(f'{reverse_node}.outputX', f'{fk_ctrls[i]}.visibility')


# Create the stretchy IK setup
def stretchyIK():
    # Calculate default distance
    def_dist = value_X_up + value_X_lo

    # Create nodes
    distance_node_01 = cmds.createNode('distanceBetween', name=f'{joints_name}_full_dist_db')
    distance_node_02 = cmds.createNode('distanceBetween', name=f'{joints_name}_pole_up_dist_db')
    distance_node_03 = cmds.createNode('distanceBetween', name=f'{joints_name}_pole_low_dist_db')
    md_node_01 = cmds.createNode('multiplyDivide', n=f'{joints_name}_stretch_md1')
    md_node_02 = cmds.createNode('multiplyDivide', n=f'{joints_name}_stretch_md2')
    condition_node = cmds.createNode('condition', n=f'{joints_name}_stretch_cd')
    blend_col_01 = cmds.createNode('blendColors', n=f'{joints_name}_stretch_bc1')
    blend_col_02 = cmds.createNode('blendColors', n=f'{joints_name}_stretch_bc2')
    blend_col_03 = cmds.createNode('blendColors', n=f'{joints_name}_stretch_bc3')
    blend_col_04 = cmds.createNode('blendColors', n=f'{joints_name}_stretch_bc4')

    # Create attributes
    stretchy_attr = cmds.addAttr(ik_wrist_control, at='bool', sn='Stretchy', keyable=1)
    lock_attr = cmds.addAttr(pv_control, at='bool', sn='Lock', keyable=1)

    # Create connections
    cmds.connectAttr(f'{ik_shoulder_control}.worldMatrix[0]', f'{distance_node_01}.inMatrix1')
    cmds.connectAttr(f'{ik_wrist_control}.worldMatrix[0]', f'{distance_node_01}.inMatrix2')
    cmds.connectAttr(f'{ik_shoulder_control}.worldMatrix[0]', f'{distance_node_02}.inMatrix1')
    cmds.connectAttr(f'{pv_control}.worldMatrix[0]', f'{distance_node_02}.inMatrix2')
    cmds.connectAttr(f'{pv_control}.worldMatrix[0]', f'{distance_node_03}.inMatrix1')
    cmds.connectAttr(f'{ik_wrist_control}.worldMatrix[0]', f'{distance_node_03}.inMatrix2')
    cmds.connectAttr(f'{distance_node_01}.distance', f'{md_node_01}.input1X')
    cmds.connectAttr(f'{distance_node_01}.distance', f'{condition_node}.firstTerm')
    cmds.connectAttr(f'{md_node_01}.outputX', f'{condition_node}.colorIfTrue.colorIfTrueR')
    cmds.connectAttr(f'{condition_node}.outColor.outColorR', f'{md_node_02}.input1X')
    cmds.connectAttr(f'{condition_node}.outColor.outColorR', f'{md_node_02}.input1Y')
    cmds.connectAttr(f'{md_node_02}.outputX', f'{blend_col_01}.color1.color1R')
    cmds.connectAttr(f'{md_node_02}.outputY', f'{blend_col_02}.color1.color1R')
    cmds.connectAttr(f'{distance_node_02}.distance', f'{blend_col_03}.color1.color1R')
    cmds.connectAttr(f'{distance_node_03}.distance', f'{blend_col_04}.color1.color1R')
    cmds.connectAttr(f'{blend_col_01}.output.outputR', f'{blend_col_03}.color2.color2R')
    cmds.connectAttr(f'{blend_col_02}.output.outputR', f'{blend_col_04}.color2.color2R')
    cmds.connectAttr(f'{blend_col_03}.output.outputR', f'{ik_jnts[1]}.translateX')
    cmds.connectAttr(f'{blend_col_04}.output.outputR', f'{ik_jnts[2]}.translateX')
    cmds.connectAttr(f'{ik_wrist_control}.Stretchy', f'{blend_col_01}.blender')
    cmds.connectAttr(f'{ik_wrist_control}.Stretchy', f'{blend_col_02}.blender')
    cmds.connectAttr(f'{pv_control}.Lock', f'{blend_col_03}.blender')
    cmds.connectAttr(f'{pv_control}.Lock', f'{blend_col_04}.blender')

    # Set values
    cmds.setAttr(f'{md_node_01}.input2X', def_dist)
    cmds.setAttr(f'{md_node_01}.operation', 2)
    cmds.setAttr(f'{condition_node}.secondTerm', def_dist)
    cmds.setAttr(f'{condition_node}.operation', 2)
    cmds.setAttr(f'{md_node_02}.input2X', value_X_up)
    cmds.setAttr(f'{md_node_02}.input2Y', value_X_lo)
    cmds.setAttr(f'{blend_col_01}.color2.color2R', value_X_up)
    cmds.setAttr(f'{blend_col_02}.color2.color2R', value_X_lo)


# Create the ribbon and its bendies
def ribbonBendies():
    # Create ribbon and crease
    ribbon_nurb = cmds.nurbsPlane(ax=[0, 0, 1], u=2, w=1, lr=0.065, name=f'nurb_ribbon_{joints_name}')[0]
    ribbon_scale = getDistance(sk_jnts[0], sk_jnts[1]) + getDistance(sk_jnts[1], sk_jnts[2])
    cmds.setAttr(f'{ribbon_nurb}.scaleX', ribbon_scale)
    cmds.setAttr(f'{ribbon_nurb}.scaleY', ribbon_scale)
    cmds.setAttr(f'{ribbon_nurb}.scaleZ', ribbon_scale)
    cmds.makeIdentity(ribbon_nurb, a=1)

    temp_null = cmds.group(empty=1)
    temp_point = cmds.pointConstraint(sk_jnts[0], sk_jnts[2], temp_null)
    temp_aim = cmds.aimConstraint(sk_jnts[2], temp_null)

    cmds.matchTransform(ribbon_nurb, temp_null)
    cmds.makeIdentity(ribbon_nurb, a=1)
    cmds.delete(ribbon_nurb, ch=1)

    cmds.delete(temp_point, temp_aim, temp_null)

    iso_sel = f'{ribbon_nurb}.u[0.5]'
    iso_01 = f'{ribbon_nurb}.u[0.52]'
    iso_02 = f'{ribbon_nurb}.u[0.48]'

    cmds.insertKnotSurface(iso_01, rpo=1)
    cmds.insertKnotSurface(iso_02, rpo=1)

    cmds.select(ribbon_nurb)
    cmds.select(cl=1)

    # Create joints and parent them
    number_of_joints = 13

    joint_list = []
    driven_group = cmds.group(n=f'grp_{ribbon_nurb}_joints', empty=1)
    cmds.select(d=1)

    for i in range(number_of_joints):
        temp_joint = cmds.joint(radius=0.2, n=f'jnt_{ribbon_nurb}_0{i + 1}')
        joint_list.append(temp_joint)
        cmds.parent(temp_joint, driven_group)
        cmds.select(d=1)

    if cmds.objExists('grp_JNTS') is True:
        cmds.parent(driven_group, 'grp_JNTS')
    else:
        cmds.group(driven_group, name='grp_JNTS')

    # Create nodes and make the connections for the POS

    # Get the shape of the NURB
    shape = cmds.listRelatives(ribbon_nurb)[0]

    counter = 0
    for i in joint_list:
        p_o_s = cmds.createNode('pointOnSurfaceInfo', n=f'{joints_name}_ribbon_pos')
        four_by_four = cmds.createNode('fourByFourMatrix', n=f'{joints_name}_ribbon_ffm')
        mult = cmds.createNode('multMatrix', n=f'{joints_name}_ribbon_mm')
        decomp = cmds.createNode('decomposeMatrix', n=f'{joints_name}_ribbon_dcm')

        cmds.connectAttr(f'{shape}.worldSpace[0]', f'{p_o_s}.inputSurface')
        cmds.connectAttr(f'{p_o_s}.result.position.positionX', f'{four_by_four}.in30')
        cmds.connectAttr(f'{p_o_s}.result.position.positionY', f'{four_by_four}.in31')
        cmds.connectAttr(f'{p_o_s}.result.position.positionZ', f'{four_by_four}.in32')
        cmds.connectAttr(f'{p_o_s}.result.normalizedNormal.normalizedNormalX', f'{four_by_four}.in20')
        cmds.connectAttr(f'{p_o_s}.result.normalizedNormal.normalizedNormalY', f'{four_by_four}.in21')
        cmds.connectAttr(f'{p_o_s}.result.normalizedNormal.normalizedNormalZ', f'{four_by_four}.in22')
        cmds.connectAttr(f'{p_o_s}.result.normalizedTangentU.normalizedTangentUX', f'{four_by_four}.in00')
        cmds.connectAttr(f'{p_o_s}.result.normalizedTangentU.normalizedTangentUY', f'{four_by_four}.in01')
        cmds.connectAttr(f'{p_o_s}.result.normalizedTangentU.normalizedTangentUZ', f'{four_by_four}.in02')
        cmds.connectAttr(f'{p_o_s}.result.normalizedTangentV.normalizedTangentVX', f'{four_by_four}.in10')
        cmds.connectAttr(f'{p_o_s}.result.normalizedTangentV.normalizedTangentVY', f'{four_by_four}.in11')
        cmds.connectAttr(f'{p_o_s}.result.normalizedTangentV.normalizedTangentVZ', f'{four_by_four}.in12')

        cmds.connectAttr(f'{four_by_four}.output', f'{mult}.matrixIn[0]')
        cmds.connectAttr(f'{i}.parentInverseMatrix', f'{mult}.matrixIn[1]')
        cmds.connectAttr(f'{mult}.matrixSum', f'{decomp}.inputMatrix')
        cmds.connectAttr(f'{decomp}.outputRotate', f'{i}.rotate')
        cmds.connectAttr(f'{decomp}.outputTranslate', f'{i}.translate')

        # Change position of joint on ribbon
        cmds.setAttr(f'{p_o_s}.turnOnPercentage', 1)

        increment = 1 / (number_of_joints - 1)

        cmds.setAttr(f'{p_o_s}.parameterV', 0.5)
        cmds.setAttr(f'{p_o_s}.parameterU', increment * counter)

        counter += 1

    # Create the controller joints by duplicating existing joints
    driver_joints = []
    counter = 1
    for i in range(5):
        temp_joint = f'jnt_{ribbon_nurb}_0{counter}'
        position = cmds.xform(temp_joint, q=1, m=1, ws=1)

        new_joint = cmds.duplicate(temp_joint)
        new_joint = new_joint[0]
        driver_joints.append(new_joint)

        cmds.xform(new_joint, m=position, ws=1)
        cmds.setAttr(f'{new_joint}.rotateX', 0)
        cmds.setAttr(f'{new_joint}.rotateY', 0)
        cmds.setAttr(f'{new_joint}.rotateZ', 0)

        counter = counter + 3

    cmds.parent(driver_joints, world=True)

    counter = 1
    for i in driver_joints:
        cmds.setAttr(i + '.radius', .5)
        cmds.rename(i, f'sk_{ribbon_nurb}_control_0{counter}')
        counter += 1

    driver_joints = []
    for i in range(5):
        driver_joints.append(f'sk_{ribbon_nurb}_control_0{i + 1}')

    if cmds.objExists('grp_JNTS') is True:
        cmds.parent(driver_joints, 'grp_JNTS')
    else:
        cmds.group(driver_joints, name='grp_JNTS')

    # Create controllers and match them to their joint
    counter = 1
    controllers_list = []
    offsets_list = []
    constraints_list = []
    for i in driver_joints:
        temp_ctrl = cmds.circle(nr=[1, 0, 0], n=f'ctrl_{ribbon_nurb}_control_0{counter}', r=3.5)
        changeColour(temp_ctrl, GREY)

        temp_cstr = cmds.group(temp_ctrl, n=f'constrain_{ribbon_nurb}_control_0{counter}')
        temp_offset = cmds.group(temp_cstr, n=f'offset_{ribbon_nurb}_control_0{counter}')
        cmds.matchTransform(temp_offset, i)
        cmds.delete(temp_ctrl, constructionHistory=True)
        temp_ctrl = temp_ctrl[0]
        controllers_list.append(temp_ctrl)
        offsets_list.append(temp_offset)
        constraints_list.append(temp_cstr)
        counter += 1

    if cmds.objExists('grp_CTRLS') is True:
        cmds.parent(offsets_list, 'grp_CTRLS')
    else:
        cmds.group(offsets_list, name='grp_CTRLS')

    # Do the matrix constraints
    counter = 0
    for i in driver_joints:
        matrixConstraint(i, controllers_list[counter], 'parent', False)
        counter += 1

    # Bind driver joints to NURB Surface
    driver_joints.append(ribbon_nurb)
    cmds.skinCluster(driver_joints, bm=0, mi=5)
    cmds.hide(driver_joints)

    # Do the matrix constraints between the controllers and the ribbon
    cmds.matchTransform(constraints_list[0], sk_jnts[0])
    cmds.matchTransform(constraints_list[2], sk_jnts[1])
    cmds.matchTransform(constraints_list[4], sk_jnts[2])

    matrixConstraint(constraints_list[0], sk_jnts[0], 'parent', True)
    matrixConstraint(constraints_list[2], sk_jnts[1], 'parent', True)
    matrixConstraint(constraints_list[4], sk_jnts[2], 'parent', True)

    # Do the blend matrix for the bendies in between

    # Create nodes
    blend_01 = cmds.createNode('blendMatrix', n=f'{joints_name}_bendies_blm1')
    cmds.setAttr(f'{blend_01}.envelope', 0.5)
    decompose_01 = cmds.createNode('decomposeMatrix', n=f'{joints_name}_bendies_dcm')
    mult_matrix_01 = cmds.createNode('multMatrix', n=f'{joints_name}_bendies_mm1')
    mult_matrix_02 = cmds.createNode('multMatrix', n=f'{joints_name}_bendies_mm2')

    # Create connections
    cmds.connectAttr(f'{controllers_list[0]}.worldMatrix[0]', f'{mult_matrix_01}.matrixIn[0]')
    cmds.connectAttr(f'{offsets_list[1]}.worldInverseMatrix[0]', f'{mult_matrix_01}.matrixIn[1]')
    cmds.connectAttr(f'{controllers_list[2]}.worldMatrix[0]', f'{mult_matrix_02}.matrixIn[0]')
    cmds.connectAttr(f'{offsets_list[1]}.worldInverseMatrix[0]', f'{mult_matrix_02}.matrixIn[1]')
    cmds.connectAttr(f'{mult_matrix_01}.matrixSum', f'{blend_01}.inputMatrix')
    cmds.connectAttr(f'{mult_matrix_02}.matrixSum', f'{blend_01}.target[0].targetMatrix')
    cmds.connectAttr(f'{blend_01}.outputMatrix', f'{decompose_01}.inputMatrix')
    cmds.connectAttr(f'{decompose_01}.outputTranslate', f'{constraints_list[1]}.translate')
    cmds.connectAttr(f'{decompose_01}.outputRotate', f'{constraints_list[1]}.rotate')

    # Create nodes
    blend_02 = cmds.createNode('blendMatrix', n=f'{joints_name}_bendies_blm2')
    cmds.setAttr(f'{blend_02}.envelope', 0.5)
    decompose_02 = cmds.createNode('decomposeMatrix', n=f'{joints_name}_bendies_dcm')
    mult_matrix_03 = cmds.createNode('multMatrix', n=f'{joints_name}_bendies_mm3')
    mult_matrix_04 = cmds.createNode('multMatrix', n=f'{joints_name}_bendies_mm4')

    # Create connections
    cmds.connectAttr(f'{controllers_list[2]}.worldMatrix[0]', f'{mult_matrix_03}.matrixIn[0]')
    cmds.connectAttr(f'{offsets_list[3]}.worldInverseMatrix[0]', f'{mult_matrix_03}.matrixIn[1]')
    cmds.connectAttr(f'{controllers_list[4]}.worldMatrix[0]', f'{mult_matrix_04}.matrixIn[0]')
    cmds.connectAttr(f'{offsets_list[3]}.worldInverseMatrix[0]', f'{mult_matrix_04}.matrixIn[1]')
    cmds.connectAttr(f'{mult_matrix_03}.matrixSum', f'{blend_02}.inputMatrix')
    cmds.connectAttr(f'{mult_matrix_04}.matrixSum', f'{blend_02}.target[0].targetMatrix')
    cmds.connectAttr(f'{blend_02}.outputMatrix', f'{decompose_02}.inputMatrix')
    cmds.connectAttr(f'{decompose_02}.outputTranslate', f'{constraints_list[3]}.translate')
    cmds.connectAttr(f'{decompose_02}.outputRotate', f'{constraints_list[3]}.rotate')

    # Create the locators for the aim constraints up objects
    loc_01 = cmds.spaceLocator(n=f'loc_{joints_name}_up_object_01')[0]
    loc_02 = cmds.spaceLocator(n=f'loc_{joints_name}_up_object_02')[0]
    offset_loc_01 = cmds.group(loc_01, n=f'offset_{joints_name}_up_object_01')
    offset_loc_02 = cmds.group(loc_02, n=f'offset_{joints_name}_up_object_02')

    cmds.matchTransform(offset_loc_01, controllers_list[1])
    cmds.matchTransform(offset_loc_02, controllers_list[3])

    cmds.parent(offset_loc_01, controllers_list[2])
    cmds.parent(offset_loc_02, controllers_list[4])

    loc_dist = getDistance(loc_01, loc_02) / 1.5

    # Set the new offsets Y distances
    temp = cmds.getAttr(f'{offset_loc_01}.translateY')
    cmds.setAttr(f'{offset_loc_01}.translateY', temp + loc_dist)
    temp = cmds.getAttr(f'{offset_loc_02}.translateY')
    cmds.setAttr(f'{offset_loc_02}.translateY', temp + loc_dist)

    # Create the bendies visibility attribute
    bendies_vis_attr = cmds.addAttr(switch_control, at='bool', ln='BendiesVis', keyable=1, defaultValue=1)
    for i in controllers_list:
        cmds.connectAttr(f'{switch_control}.BendiesVis', f'{i}.visibility')

    # Create the MISC group or parent to ribbon to it and hide it
    if cmds.objExists('grp_MISC') is True:
        cmds.parent(ribbon_nurb, 'grp_MISC')
    else:
        cmds.group(ribbon_nurb, name='grp_MISC')

    cmds.hide(ribbon_nurb)

    # Constrain the switch control to the last ribbon controller
    matrixConstraint(switch_offset, controllers_list[4], 'parent', True)


# Run the script
def runScript(*args):
    global joints_name

    if len(cmds.textField('limbs_name', query=True, text=True)) == 0:
        joints_name = 'temp_limb'
    else:
        joints_name = cmds.textField('limbs_name', query=True, text=True)

    userSel()
    createJointsControllers()
    blendingSwitch()

    if cmds.checkBox('stretchy_checkbox', q=1, v=1) == 1:
        stretchyIK()

    if cmds.checkBox('ribbon_checkbox', q=1, v=1) == 1:
        ribbonBendies()

    cmds.select(cl=1)


# Create the UI
def ikfkSwitchUI():
    global joints_name

    # Create window
    if cmds.window('ikfk_switch_window', ex=1) == True:
        cmds.deleteUI('ikfk_switch_window')

    ikfk_switch_window = cmds.window('ikfk_switch_window', title='IK FK Limb Creator v1.5', w=220, h=175,
                                     mnb=False, mxb=False, sizeable=False)

    # Create main Layout
    main_layout = cmds.formLayout(nd=100)

    # Create title
    title = cmds.text(label='IK FK Limb Creator', font='boldLabelFont')

    # Create Separator(s)
    separator_01 = cmds.separator(h=5, style='shelf')

    # Create text input
    limbs_name = cmds.textField('limbs_name', pht='temp_limb', width=100)
    limbs_name_title = cmds.text(label='Limb Name')

    # Create the checkboxes
    ribbon_checkbox = cmds.checkBox('ribbon_checkbox', v=1, label='Ribbon Deformers')
    stretchy_checkbox = cmds.checkBox('stretchy_checkbox', v=1, label='Stretchy IK')

    # Create the creation button
    create_button = cmds.button(label='CREATE', command=runScript)

    # Adjust layout
    cmds.formLayout(main_layout, e=True,
                    attachForm=[(title, 'top', 7), (title, 'left', 5), (title, 'right', 5),

                                (separator_01, 'left', 5), (separator_01, 'right', 5),

                                (create_button, 'left', 5), (create_button, 'right', 5), (create_button, 'bottom', 5),

                                (limbs_name_title, 'left', 27), (limbs_name, 'left', 91),

                                (stretchy_checkbox, 'left', 12), (ribbon_checkbox, 'left', 93)
                                ],

                    attachControl=[(separator_01, 'top', 5, title),

                                   (limbs_name, 'top', 15, separator_01),

                                   (limbs_name_title, 'top', 17, separator_01),

                                   (stretchy_checkbox, 'top', 10, limbs_name),

                                   (ribbon_checkbox, 'top', 10, limbs_name),

                                   (create_button, 'top', 15, stretchy_checkbox)
                                   ])

    cmds.showWindow(ikfk_switch_window)


ikfkSwitchUI()
