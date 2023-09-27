# ------------------------------------------------------------------------------------------
#
# ----------------------  Quick POC Script v1.0 by Elio Molinaro  --------------------------
#
# ------------------------------------------------------------------------------------------

"""Create a point on curve from a selected curve"""

import maya.cmds as cmds


# main creation function
def createFunction(curve, object):

    # get curve's shape
    crv_shape = cmds.listRelatives(curve, s=1)[0]

    #Create the attributes on the constrained object
    cmds.addAttr(object, at='float', ln='Position', min=0, max=10, k=1)
    cmds.addAttr(object, at='bool', ln='Rotation', dv=1, k=1)

    # Create the nodes
    mult_div_01 = cmds.createNode('multiplyDivide', n='poc_util_md_01')
    cmds.setAttr(f'{mult_div_01}.input2X', 0.1)
    mult_div_02 = cmds.createNode('multiplyDivide', n='poc_util_md_02')
    decomp_matrix = cmds.createNode('decomposeMatrix', n='poc_util_dcm')
    four_by_four = cmds.createNode('fourByFourMatrix', n='poc_util_ffm')
    p_o_c = cmds.createNode('pointOnCurveInfo', n='poc_util_poc')
    cmds.setAttr(f'{p_o_c}.turnOnPercentage', 1)

    # Create connections
    cmds.connectAttr(f'{object}.Position', f'{mult_div_01}.input1.input1X')
    cmds.connectAttr(f'{mult_div_01}.outputX', f'{p_o_c}.parameter')
    cmds.connectAttr(f'{crv_shape}.worldSpace', f'{p_o_c}.inputCurve')
    cmds.connectAttr(f'{p_o_c}.result.position.positionX', f'{four_by_four}.in30')
    cmds.connectAttr(f'{p_o_c}.result.position.positionY', f'{four_by_four}.in31')
    cmds.connectAttr(f'{p_o_c}.result.position.positionZ', f'{four_by_four}.in32')
    cmds.connectAttr(f'{p_o_c}.result.tangent.tangentX', f'{four_by_four}.in10')
    cmds.connectAttr(f'{p_o_c}.result.tangent.tangentY', f'{four_by_four}.in11')
    cmds.connectAttr(f'{p_o_c}.result.tangent.tangentZ', f'{four_by_four}.in12')
    cmds.connectAttr(f'{p_o_c}.result.normal.normalX', f'{four_by_four}.in00')
    cmds.connectAttr(f'{p_o_c}.result.normal.normalY', f'{four_by_four}.in01')
    cmds.connectAttr(f'{p_o_c}.result.normal.normalZ', f'{four_by_four}.in02')
    cmds.connectAttr(f'{four_by_four}.output', f'{decomp_matrix}.inputMatrix')
    cmds.connectAttr(f'{decomp_matrix}.outputTranslate', f'{object}.translate')
    cmds.connectAttr(f'{decomp_matrix}.outputRotate', f'{mult_div_02}.input1')
    cmds.connectAttr(f'{object}.Rotation', f'{mult_div_02}.input2X')
    cmds.connectAttr(f'{object}.Rotation', f'{mult_div_02}.input2Y')
    cmds.connectAttr(f'{object}.Rotation', f'{mult_div_02}.input2Z')
    cmds.connectAttr(f'{mult_div_02}.output', f'{object}.rotate')


# Main function that runs the script or throws an error if conditions are not met
def runScript():
    user_sel = cmds.ls(sl=1)

    # Check when one object is selected if it's a curve
    if len(user_sel) == 1:
        sel_shape = cmds.listRelatives(user_sel, s=1)
        sel_type = cmds.nodeType(sel_shape)

        if sel_type == 'nurbsCurve':
            object = cmds.spaceLocator(n='loc_util_poc_01')[0]
            createFunction(user_sel[0], object)
        else:
            cmds.error('Please only select one curve and an object or one only curve')

    # Check when two objects are selected if one of them is a curve
    elif len(user_sel) == 2:
        sel_shapes = []
        sel_types = []
        for i in user_sel:
            temp_shape = cmds.listRelatives(i, s=1)
            sel_shapes.append(temp_shape)
            temp_type = cmds.nodeType(temp_shape)
            sel_types.append(temp_type)
            if temp_type == 'nurbsCurve':
                sel_has_curve = True

        # Decides in what case should each script run
        if sel_has_curve is True:
            if sel_types[0] == 'nurbsCurve':
                createFunction(user_sel[0], user_sel[1])
            elif sel_types[1] == 'nurbsCurve':
                createFunction(user_sel[1], user_sel[0])
        else:
            cmds.error('Please only select one curve and an object or one only curve')

    else:
        cmds.error('Please only select one curve and an object or one only curve')


runScript()
