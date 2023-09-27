# ------------------------------------------------------------------------------------------
#
# --------------------  Quick Rivet Script v1.0 by Elio Molinaro  -------------------------
#
# ------------------------------------------------------------------------------------------

"""Create rivets between the selected edges/vertices"""

import maya.cmds as cmds

# Create the user selection logic
def userSel():
    global loc
    global object_shape

    # Check if user selection is made out of edges or faces
    user_sel = cmds.ls(sl=1)

    if len(user_sel) == 1 and len(user_sel[0].split(':')) == 1:
        temp_split = user_sel[0].split('.')
        comp_type = temp_split[1].split('[')[0]
        temp_number = temp_split[1].split('[')[1]
        comp_number_01 = int(temp_number.split(']')[0])
        comp_number_02 = int(temp_number.split(']')[0])+20

        if comp_type != 'f':
            cmds.error('Please select one face or 2 edges')

    elif len(user_sel) == 1 and len(user_sel[0].split(':')) == 2:
        temp_split = user_sel[0].split('.')
        comp_type = temp_split[1].split('[')[0]
        temp_number = temp_split[1].split('[')[1]
        temp_number = temp_number.split(']')[0]
        comp_number_01 = int(temp_number.split(':')[0])
        comp_number_02 = int(temp_number.split(':')[1])

        if comp_type != 'e':
            cmds.error('Please select one face or 2 edges')

    elif len(user_sel) == 2 and len(user_sel[0].split(':')) == 1 and len(user_sel[1].split(':')) == 1:
        temp_split = user_sel[0].split('.')
        comp_type = temp_split[1].split('[')[0]
        temp_number = user_sel[0].split('[')[1]
        comp_number_01 = int(temp_number.split(']')[0])
        temp_number = user_sel[1].split('[')[1]
        comp_number_02 = int(temp_number.split(']')[0])

        if comp_type != 'e':
            cmds.error('Please select one face or 2 edges')

    else:
        cmds.error('Please select one face or 2 edges')

    # Create the rivet locator and its attributes
    loc = cmds.spaceLocator(n='loc_rivet_util_01')[0]
    object = user_sel[0].split('.')[0]
    object_shape = cmds.listRelatives(object, s=1)[0]
    edge_max = cmds.polyEvaluate(object, e=1)
    cmds.addAttr(loc, at='long', ln='Edge_Index_0', min=0, max=edge_max, dv=comp_number_01, k=1)
    cmds.addAttr(loc, at='long', ln='Edge_Index_1', min=0, max=edge_max, dv=comp_number_02, k=1)
    cmds.addAttr(loc, at='float2', ln='UV')
    cmds.addAttr(loc, at='float', ln='U', max=1, min=0, dv=0.5, p='UV', k=1)
    cmds.addAttr(loc, at='float', ln='V', max=1, min=0, dv=0.5, p='UV', k=1)


# Create the rivet
def createRivet():
    # Create nodes
    cfme_01 = cmds.createNode('curveFromMeshEdge', n='rivet_util_cfme')
    cfme_02 = cmds.createNode('curveFromMeshEdge', n='rivet_util_cfme')
    loft = cmds.createNode('loft', n='rivet_util_loft')
    p_o_s = cmds.createNode('pointOnSurfaceInfo', n='rivet_util_pos')
    cmds.setAttr(f'{p_o_s}.turnOnPercentage', 1)
    four_by_four = cmds.createNode('fourByFourMatrix', n='rivet_util_ffm')
    decomp_matrix = cmds.createNode('decomposeMatrix', n='rivet_util_dcm')

    # Create connections
    cmds.connectAttr(f'{loc}.Edge_Index_0', f'{cfme_01}.edgeIndex[0]')
    cmds.connectAttr(f'{loc}.Edge_Index_1', f'{cfme_02}.edgeIndex[1]')
    cmds.connectAttr(f'{object_shape}.worldMesh', f'{cfme_01}.inputMesh')
    cmds.connectAttr(f'{object_shape}.worldMesh', f'{cfme_02}.inputMesh')
    cmds.connectAttr(f'{cfme_01}.outputCurve', f'{loft}.inputCurve[0]')
    cmds.connectAttr(f'{cfme_02}.outputCurve', f'{loft}.inputCurve[1]')
    cmds.connectAttr(f'{loft}.outputSurface', f'{p_o_s}.inputSurface')
    cmds.connectAttr(f'{loc}.U', f'{p_o_s}.parameterU')
    cmds.connectAttr(f'{loc}.V', f'{p_o_s}.parameterV')
    cmds.connectAttr(f'{p_o_s}.result.position.positionX', f'{four_by_four}.in30')
    cmds.connectAttr(f'{p_o_s}.result.position.positionY', f'{four_by_four}.in31')
    cmds.connectAttr(f'{p_o_s}.result.position.positionZ', f'{four_by_four}.in32')
    cmds.connectAttr(f'{p_o_s}.result.tangentV.tangentVx', f'{four_by_four}.in20')
    cmds.connectAttr(f'{p_o_s}.result.tangentV.tangentVy', f'{four_by_four}.in21')
    cmds.connectAttr(f'{p_o_s}.result.tangentV.tangentVz', f'{four_by_four}.in22')
    cmds.connectAttr(f'{p_o_s}.result.tangentU.tangentUx', f'{four_by_four}.in10')
    cmds.connectAttr(f'{p_o_s}.result.tangentU.tangentUy', f'{four_by_four}.in11')
    cmds.connectAttr(f'{p_o_s}.result.tangentU.tangentUz', f'{four_by_four}.in12')
    cmds.connectAttr(f'{p_o_s}.result.normal.normalX', f'{four_by_four}.in00')
    cmds.connectAttr(f'{p_o_s}.result.normal.normalY', f'{four_by_four}.in01')
    cmds.connectAttr(f'{p_o_s}.result.normal.normalZ', f'{four_by_four}.in02')
    cmds.connectAttr(f'{four_by_four}.output', f'{decomp_matrix}.inputMatrix')
    cmds.connectAttr(f'{decomp_matrix}.outputTranslate', f'{loc}.translate')
    cmds.connectAttr(f'{decomp_matrix}.outputRotate', f'{loc}.rotate')


# Execute commands
userSel()
createRivet()
