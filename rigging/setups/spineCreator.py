# ------------------------------------------------------------------------------------------
#
# --------------------  IK FK Spine Script v1.1 by Elio Molinaro  -------------------------
#
# ------------------------------------------------------------------------------------------

"""Spine creator based on one joint with 3 children joints"""

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
    global sk_jnts_orients

    sel = cmds.ls(sl=1)

    if len(sel) == 1:
        sk_jnt_01 = sel[0]
        sk_jnt_02 = cmds.listRelatives(sk_jnt_01, children=1)[0]
        sk_jnt_03 = cmds.listRelatives(sk_jnt_02, children=1)[0]
        sk_jnt_04 = cmds.listRelatives(sk_jnt_03, children=1)[0]

        sk_jnt_01 = cmds.rename(sk_jnt_01, f'sk_{joints_name}_cog')
        sk_jnt_02 = cmds.rename(sk_jnt_02, f'sk_{joints_name}_01')
        sk_jnt_03 = cmds.rename(sk_jnt_03, f'sk_{joints_name}_02')
        sk_jnt_04 = cmds.rename(sk_jnt_04, f'sk_{joints_name}_03')

        if cmds.nodeType(sk_jnt_01) != 'joint' or cmds.nodeType(sk_jnt_02) != 'joint' or cmds.nodeType(
                sk_jnt_03) != 'joint' or cmds.nodeType(sk_jnt_04) != 'joint':
            cmds.error('Please only select one joint that has 3 children joints')
        else:
            sk_jnts = [sk_jnt_01, sk_jnt_02, sk_jnt_03, sk_jnt_04]

    else:
        cmds.error('Please only select one joint that has 3 children joints')

    # Get the orientation of the sk joints
    sk_jnt_01_orient = [cmds.getAttr(f'{sk_jnts[1]}.jointOrientX'), cmds.getAttr(f'{sk_jnts[1]}.jointOrientY'), cmds.getAttr(f'{sk_jnts[1]}.jointOrientZ')]
    sk_jnt_02_orient = [cmds.getAttr(f'{sk_jnts[2]}.jointOrientX'), cmds.getAttr(f'{sk_jnts[2]}.jointOrientY'), cmds.getAttr(f'{sk_jnts[2]}.jointOrientZ')]
    sk_jnt_03_orient = [cmds.getAttr(f'{sk_jnts[3]}.jointOrientX'), cmds.getAttr(f'{sk_jnts[3]}.jointOrientY'), cmds.getAttr(f'{sk_jnts[3]}.jointOrientZ')]

    sk_jnts_orients = [sk_jnt_01_orient, sk_jnt_02_orient, sk_jnt_03_orient]



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
    global fk_ctrls
    global ik_ctrls
    global cog_ctrl

    # Create IK joints
    ik_jnt_01 = cmds.duplicate(sk_jnts[1], n=f'ik_{joints_name}_01', po=1)[0]
    ik_jnt_02 = cmds.duplicate(sk_jnts[2], n=f'ik_{joints_name}_01', po=1)[0]
    ik_jnt_03 = cmds.duplicate(sk_jnts[3], n=f'ik_{joints_name}_01', po=1)[0]

    ik_jnts = [ik_jnt_01, ik_jnt_02, ik_jnt_03]
    cmds.hide(ik_jnt_01)
    cmds.parent(ik_jnts, w=1)

    cmds.parent(ik_jnt_01, sk_jnts[0])
    cmds.parent(ik_jnt_02, sk_jnts[0])
    cmds.parent(ik_jnt_03, sk_jnts[0])

    # Create FK joints
    fk_jnt_01 = cmds.duplicate(sk_jnts[1], n=f'fk_{joints_name}_01', po=1)[0]
    fk_jnt_02 = cmds.duplicate(sk_jnts[2], n=f'fk_{joints_name}_01', po=1)[0]
    fk_jnt_03 = cmds.duplicate(sk_jnts[3], n=f'fk_{joints_name}_01', po=1)[0]

    fk_jnts = [fk_jnt_01, fk_jnt_02, fk_jnt_03]
    cmds.hide(fk_jnt_01)
    cmds.parent(fk_jnts, w=1)

    cmds.parent(fk_jnt_03, fk_jnt_02)
    cmds.parent(fk_jnt_02, fk_jnt_01)
    cmds.parent(fk_jnt_01, sk_jnts[0])

    # Create the cog controller
    cog_ctrl = mm.eval('curve -d 1 -p -0.5214 0 0.5214 -p -1.056 0 0.363 -p -0.99 0 0.66 -p -1.65 0 0 -p -0.99 0 -0.66 -p -1.056 0 -0.363 -p -0.5214 0 -0.5214 -p -0.363 0 -1.056 -p -0.66 0 -0.99 -p 0 0 -1.65 -p 0.66 0 -0.99 -p 0.363 0 -1.056 -p 0.5214 0 -0.5214 -p 1.056 0 -0.363 -p 0.99 0 -0.66 -p 1.65 0 0 -p 0.99 0 0.66 -p 1.056 0 0.363 -p 0.5214 0 0.5214 -p 0.363 0 1.056 -p 0.66 0 0.99 -p 0 0 1.65 -p -0.66 0 0.99 -p -0.363 0 1.056 -p -0.5214 0 0.5214 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 -k 18 -k 19 -k 20 -k 21 -k 22 -k 23 -k 24 ;')
    cmds.setAttr(f'{cog_ctrl}.scaleX', 18)
    cmds.setAttr(f'{cog_ctrl}.scaleY', 18)
    cmds.setAttr(f'{cog_ctrl}.scaleZ', 18)
    cmds.makeIdentity(cog_ctrl, a=1)
    cog_ctrl = cmds.rename(cog_ctrl, f'ctrl_{joints_name}_cog')
    cog_offset = cmds.group(cog_ctrl, n=f'offset_{joints_name}_cog')
    cmds.matchTransform(cog_offset, sk_jnts[0], pos=1)
    cmds.addAttr(cog_ctrl, at='double', nn='IK FK Switch', sn='ikFkSwitch', min=0, max=10, dv=0, keyable=1)
    rmanAttrsHide(cog_ctrl)

    changeColour(cog_ctrl, 13)

    # Create the fk controllers
    fk_ctrl_01 = cmds.circle(nr=[0, 1, 0], r=15, n=f'ctrl_{joints_name}_fk_01', ch=0)[0]
    fk_offset_01 = cmds.group(fk_ctrl_01, n=f'offset_{joints_name}_fk_01')
    cmds.matchTransform(fk_offset_01, sk_jnts[1], pos=1)
    rmanAttrsHide(fk_ctrl_01)

    fk_ctrl_02 = cmds.circle(nr=[0, 1, 0], r=15, n=f'ctrl_{joints_name}_fk_02', ch=0)[0]
    fk_offset_02 = cmds.group(fk_ctrl_02, n=f'offset_{joints_name}_fk_02')
    cmds.matchTransform(fk_offset_02, sk_jnts[2], pos=1)
    rmanAttrsHide(fk_ctrl_02)

    fk_ctrl_03 = cmds.circle(nr=[0, 1, 0], r=15, n=f'ctrl_{joints_name}_fk_03', ch=0)[0]
    fk_offset_03 = cmds.group(fk_ctrl_03, n=f'offset_{joints_name}_fk_03')
    cmds.matchTransform(fk_offset_03, sk_jnts[3], pos=1)
    rmanAttrsHide(fk_ctrl_03)

    cmds.parent(fk_offset_03, fk_ctrl_02)
    cmds.parent(fk_offset_02, fk_ctrl_01)
    cmds.parent(fk_offset_01, cog_ctrl)

    fk_ctrls = [fk_ctrl_01, fk_ctrl_02, fk_ctrl_03]

    changeColour(fk_ctrl_01, 17)
    changeColour(fk_ctrl_02, 17)
    changeColour(fk_ctrl_03, 17)

    # Parent the controllers to their joint
    matrixConstraint(fk_jnt_01, fk_ctrl_01, 'parent', False)
    matrixConstraint(fk_jnt_02, fk_ctrl_02, 'parent', False)
    matrixConstraint(fk_jnt_03, fk_ctrl_03, 'parent', False)

    # Create the ik controllers
    ik_ctrl_01 = mm.eval('curve -d 1 -p 1 0 -1 -p 1 0 1 -p -1 0 1 -p -1 0 -1 -p 1 0 -1 -k 0 -k 1 -k 2 -k 3 -k 4 ;')
    cmds.setAttr(f'{ik_ctrl_01}.scaleX', 12)
    cmds.setAttr(f'{ik_ctrl_01}.scaleY', 12)
    cmds.setAttr(f'{ik_ctrl_01}.scaleZ', 12)
    cmds.makeIdentity(ik_ctrl_01, a=1)
    ik_ctrl_01 = cmds.rename(ik_ctrl_01, f'ctrl_{joints_name}_ik_01')
    ik_offset_01 = cmds.group(ik_ctrl_01, n=f'offset_{joints_name}_ik_01')
    cmds.matchTransform(ik_offset_01, sk_jnts[1], pos=1)
    rmanAttrsHide(ik_ctrl_01)

    ik_ctrl_02 = mm.eval('curve -d 1 -p 1 0 -1 -p 1 0 1 -p -1 0 1 -p -1 0 -1 -p 1 0 -1 -k 0 -k 1 -k 2 -k 3 -k 4 ;')
    cmds.setAttr(f'{ik_ctrl_02}.scaleX', 12)
    cmds.setAttr(f'{ik_ctrl_02}.scaleY', 12)
    cmds.setAttr(f'{ik_ctrl_02}.scaleZ', 12)
    cmds.makeIdentity(ik_ctrl_02, a=1)
    ik_ctrl_02 = cmds.rename(ik_ctrl_02, f'ctrl_{joints_name}_ik_02')
    ik_offset_02 = cmds.group(ik_ctrl_02, n=f'offset_{joints_name}_ik_02')
    cmds.matchTransform(ik_offset_02, sk_jnts[2], pos=1)
    rmanAttrsHide(ik_ctrl_02)

    ik_ctrl_03 = mm.eval('curve -d 1 -p 1 0 -1 -p 1 0 1 -p -1 0 1 -p -1 0 -1 -p 1 0 -1 -k 0 -k 1 -k 2 -k 3 -k 4 ;')
    cmds.setAttr(f'{ik_ctrl_03}.scaleX', 12)
    cmds.setAttr(f'{ik_ctrl_03}.scaleY', 12)
    cmds.setAttr(f'{ik_ctrl_03}.scaleZ', 12)
    cmds.makeIdentity(ik_ctrl_03, a=1)
    ik_ctrl_03 = cmds.rename(ik_ctrl_03, f'ctrl_{joints_name}_ik_03')
    ik_offset_03 = cmds.group(ik_ctrl_03, n=f'offset_{joints_name}_ik_03')
    cmds.matchTransform(ik_offset_03, sk_jnts[3], pos=1)
    rmanAttrsHide(ik_ctrl_03)

    cmds.parent(ik_offset_01, cog_ctrl)
    cmds.parent(ik_offset_02, cog_ctrl)
    cmds.parent(ik_offset_03, cog_ctrl)

    changeColour(ik_ctrl_01, 17)
    changeColour(ik_ctrl_02, 17)
    changeColour(ik_ctrl_03, 17)

    ik_ctrls = [ik_ctrl_01, ik_ctrl_02, ik_ctrl_03]

    # Parent the controllers to their joint
    matrixConstraint(ik_jnt_01, ik_ctrl_01, 'parent', False)
    matrixConstraint(ik_jnt_02, ik_ctrl_02, 'parent', False)
    matrixConstraint(ik_jnt_03, ik_ctrl_03, 'parent', False)

    # Check if CTRLS group exists and parent to it or create it
    if cmds.objExists('grp_CTRLS') is True:
        cmds.parent(cog_offset, 'grp_CTRLS')
    else:
        cmds.group(empty=1, name='grp_CTRLS')
        cmds.parent(cog_offset, 'grp_CTRLS')


# Create blending between FK and IK
def blendingSwitch():

    md_node = cmds.createNode('multiplyDivide', n=f'{joints_name}_switch_mm')
    reverse_node = cmds.createNode('reverse', n=f'{joints_name}_switch_rv')
    cmds.connectAttr(f'{cog_ctrl}.ikFkSwitch', f'{md_node}.input1.input1X')
    cmds.connectAttr(f'{cog_ctrl}.ikFkSwitch', f'{ik_ctrls[0]}.visibility')
    cmds.connectAttr(f'{cog_ctrl}.ikFkSwitch', f'{ik_ctrls[1]}.visibility')
    cmds.connectAttr(f'{cog_ctrl}.ikFkSwitch', f'{ik_ctrls[2]}.visibility')
    cmds.connectAttr(f'{md_node}.outputX', f'{reverse_node}.inputX')
    cmds.setAttr(f'{md_node}.input2X', 10)
    cmds.setAttr(f'{md_node}.operation', 2)

    for i in range(3):
        blend_matrix = cmds.createNode('blendMatrix', n=f'{joints_name}_switch{i+1}_blm')
        cmds.connectAttr(f'{fk_jnts[i]}.worldMatrix[0]', f'{blend_matrix}.inputMatrix')
        cmds.connectAttr(f'{ik_jnts[i]}.worldMatrix[0]', f'{blend_matrix}.target[0].targetMatrix')
        cmds.connectAttr(f'{blend_matrix}.outputMatrix', f'{sk_jnts[i+1]}.offsetParentMatrix')
        cmds.setAttr(f'{sk_jnts[i+1]}.translateX', 0)
        cmds.setAttr(f'{sk_jnts[i+1]}.translateY', 0)
        cmds.setAttr(f'{sk_jnts[i+1]}.translateZ', 0)
        cmds.setAttr(f'{sk_jnts[i+1]}.jointOrientX', 0)
        cmds.setAttr(f'{sk_jnts[i+1]}.jointOrientY', 0)
        cmds.setAttr(f'{sk_jnts[i+1]}.jointOrientZ', 0)
        cmds.setAttr(f'{sk_jnts[i+1]}.inheritsTransform', 0)
        cmds.connectAttr(f'{md_node}.outputX', f'{blend_matrix}. envelope')
        cmds.connectAttr(f'{reverse_node}.outputX', f'{fk_ctrls[i]}.visibility')


# Create the ribbon
def ribbon():

    # Create ribbon and crease
    ribbon_nurb = cmds.nurbsPlane(ax=[0, 1, 0], u=6, w=1, lr=0.065, name=f'nurb_{joints_name}_ribbon')[0]
    ribbon_scale = getDistance(sk_jnts[1], sk_jnts[2]) + getDistance(sk_jnts[2], sk_jnts[3])
    cmds.setAttr(f'{ribbon_nurb}.scaleX', ribbon_scale)
    cmds.setAttr(f'{ribbon_nurb}.scaleY', ribbon_scale)
    cmds.setAttr(f'{ribbon_nurb}.scaleZ', ribbon_scale)
    cmds.makeIdentity(ribbon_nurb, a=1)

    temp_null = cmds.group(empty=1)
    temp_point = cmds.pointConstraint(sk_jnts[1], sk_jnts[3], temp_null)
    temp_aim = cmds.aimConstraint(sk_jnts[3], temp_null)

    cmds.matchTransform(ribbon_nurb, temp_null)
    cmds.makeIdentity(ribbon_nurb, a=1)
    cmds.delete(ribbon_nurb, ch=1)

    cmds.delete(temp_point, temp_aim, temp_null)

    cmds.select(cl=1)

    # Create joints and parent them
    number_of_joints = 7

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

    # Create the temporary driver joints by duplicating existing joints
    driver_joints = []
    counter = 1
    for i in range(3):
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
    for i in range(3):
        driver_joints.append(f'sk_{ribbon_nurb}_control_0{i + 1}')

    if cmds.objExists('grp_JNTS') is True:
        cmds.parent(driver_joints, 'grp_JNTS')
    else:
        cmds.group(driver_joints, name='grp_JNTS')

    # Bind driver joints to NURB Surface
    cmds.skinCluster(driver_joints, ribbon_nurb, bm=0, mi=5)

    # Match transform the bind temp joints to the sk joints
    for i in range(len(driver_joints)):
        #cmds.matchTransform(driver_joints[i], sk_jnts[i+1])
        target = cmds.xform(sk_jnts[i+1], q=1, m=1, ws=1)
        cmds.xform(driver_joints[i], m=target, ws=1)

    # delete the history of the ribbon and delete the bind joints
    cmds.delete(ribbon_nurb, ch=1)
    cmds.delete(driver_joints)

    # Bind the ribbon to the sk joints
    skin_cluster = cmds.skinCluster(sk_jnts[1], sk_jnts[3], sk_jnts[2], ribbon_nurb, bm=0, mi=2, ns=6, ihs=1, n=f'skinCluster_{joints_name}')[0]

    # remove unwanted influences
    cmds.skinCluster(skin_cluster, e=1, ri=sk_jnts[0])
    cmds.skinCluster(skin_cluster, e=1, ri=ik_jnts)
    cmds.skinCluster(skin_cluster, e=1, ri=fk_jnts)

    # Edit the skinning values
    cmds.skinPercent(skin_cluster, f'nurb_{joints_name}_ribbon.cv[0:2][0:3]', tv=[sk_jnts[1], 1])
    cmds.skinPercent(skin_cluster, f'nurb_{joints_name}_ribbon.cv[3][0:3]', tv=[(sk_jnts[1], 0.5), (sk_jnts[2], 0.5)])
    cmds.skinPercent(skin_cluster, f'nurb_{joints_name}_ribbon.cv[4][0:3]', tv=[sk_jnts[2], 1])
    cmds.skinPercent(skin_cluster, f'nurb_{joints_name}_ribbon.cv[5][0:3]', tv=[(sk_jnts[2], 0.5), (sk_jnts[3], 0.5)])
    cmds.skinPercent(skin_cluster, f'nurb_{joints_name}_ribbon.cv[6:8][0:3]', tv=[sk_jnts[3], 1])


    # Create the MISC group or parent to ribbon to it and hide it
    if cmds.objExists('grp_MISC') is True:
        cmds.parent(ribbon_nurb, 'grp_MISC')
    else:
        cmds.group(ribbon_nurb, name='grp_MISC')

    cmds.hide(ribbon_nurb)


# Run the script
def runScript(*args):

    userSel()
    createJointsControllers()
    blendingSwitch()
    ribbon()

    cmds.select(cl=1)


# Create the UI
def ikfkSpineUI():

    global joints_name

    result = cmds.promptDialog(
        title='IK FK Spine Tool v1.1',
        message='Spine Name:',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel')

    if result == 'OK':
        if len(cmds.promptDialog(query=True, text=True)) == 0:
            joints_name = 'spine'
        else:
            joints_name = cmds.promptDialog(query=True, text=True)

        runScript()


ikfkSpineUI()
