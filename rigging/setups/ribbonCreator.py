#------------------------------------------------------------------------------------------
#
#----------------  Ribbon Automation Script v3.0 by Elio Molinaro  ------------------------
#
#------------------------------------------------------------------------------------------

"""Creates Ribbons for you"""

import maya.cmds as cmds
import pymel.core as pm


def driversCheckboxOn(*args):
    cmds.checkBox('drivers_checkbox', edit=1, value=1, ed=0)

def driversCheckboxOff(*args):
    cmds.checkBox('drivers_checkbox', edit=1, value=1, ed=1)


# Prepare the ribbon 
def ribbonPrep(x):

    global main_side

    spans_U = cmds.getAttr(f'{user_shape}.spansU')
    spans_V = cmds.getAttr(f'{user_shape}.spansV')

    if spans_U != 1 or spans_V != 1:
        if spans_U > spans_V:
            main_side = 'U'
        elif spans_U < spans_V:
            main_side = 'V'

    else:
        scaleX = cmds.getAttr(f'{user_sel}.scaleX')
        scaleZ = cmds.getAttr(f'{user_sel}.scaleZ')

        if scaleX > scaleZ:
            main_side = 'U'
        elif scaleX < scaleZ:
            main_side = 'V'
        else:
            cmds.error("Your ribbon can't be square shaped")

        if x != 0:
            number_of_spans = x
        else:
            number_of_spans = 2 * (number_of_controllers - 1)

        shape = cmds.listRelatives(user_sel)[0]
        make = cmds.listConnections(shape)[1]

        cmds.setAttr(f'{make}.patches{main_side}', number_of_spans)

        cmds.makeIdentity(user_sel, a=1)
        cmds.delete(user_sel, ch=1)


# Define the joints number equation
def num_joints(x):

    global number_of_joints

    number_of_joints = 4 * (x-1) + 1


# Define the NURBS selection function
def selNurb():
    global user_sel
    global user_shape

    user_sel = cmds.ls(sl=True)

    if len(user_sel) != 1:
        cmds.error('Please only select one NURB Surface')
    else:
        user_sel = user_sel[0]
        user_shape = cmds.listRelatives(user_sel, shapes=1)[0]


# Create matrix constraint function
def matrixConstraint(child, parent):

    # Get child parent
    child_parent = cmds.listRelatives(child, p=True)
    child_parent = child_parent[0]

    # Create nodes
    mult_matrix = cmds.createNode('multMatrix', n=f'{ribbon_name}_driver_mm')
    decompose_matrix = cmds.createNode('decomposeMatrix', n=f'{ribbon_name}_driver_dcm')

    # Make connections
    cmds.connectAttr(f'{parent}.worldMatrix[0]', f'{mult_matrix}.matrixIn[0]')
    cmds.connectAttr(f'{child_parent}.worldInverseMatrix[0]', f'{mult_matrix}.matrixIn[1]')
    cmds.connectAttr(f'{mult_matrix}.matrixSum', f'{decompose_matrix}.inputMatrix')
    cmds.connectAttr(f'{decompose_matrix}.outputTranslate', f'{child}.translate')
    cmds.connectAttr(f'{decompose_matrix}.outputRotate', f'{child}.rotate')
    cmds.connectAttr(f'{decompose_matrix}.outputScale', f'{child}.scale')

    # Reset joint orientation
    cmds.setAttr(f'{child}.jointOrientX', 0)
    cmds.setAttr(f'{child}.jointOrientY', 0)
    cmds.setAttr(f'{child}.jointOrientZ', 0)


# Define the follicles function
def folliclesRibbon():

    global controllers_list
    global ribbon_name

    # Handling text field variables
    if len(cmds.textField('name_text_field', query=True, text=True)) == 0:
        ribbon_name = 'temp_ribbon'
    else:
        ribbon_name = cmds.textField('name_text_field', query=True, text=True)

    if len(cmds.textField('ctrls_text_field', query=True, text=True)) == 0:
        number_of_controllers = 5
    else:
        number_of_controllers = int(cmds.textField('ctrls_text_field', query=True, text=True))

    num_joints(number_of_controllers)
    selNurb()
    ribbonPrep(0)

    # Create the hair system and delete unwanted stuff
    if main_side == 'U':
        pm.language.Mel.eval(f"createHair {number_of_joints} 1 10 0 0 1 0 5 0 1 1 1;")
    elif main_side == 'V':
        pass
    pm.language.Mel.eval(f"createHair 1 {number_of_joints}  10 0 0 1 0 5 0 1 1 1;")

    temp_delete = ['hairSystem1', 'pfxHair1', 'nucleus1']
    cmds.delete(temp_delete)

    follicles_list = cmds.listRelatives('hairSystem1Follicles', children=True)

    cmds.rename('hairSystem1Follicles', 'grp_follicles_' + ribbon_name)
    temp_delete = []

    for i in range(number_of_joints):
        temp_delete.append(f'curve{i+1}')

    cmds.delete(temp_delete)


    # Create joints and parent them
    joint_list = []
    for i in range(number_of_joints):
        joint_list.append(cmds.joint(radius=0.2))
        cmds.select(clear=True)


    # Parent joints to follicles and reset transforms
    for i in range(number_of_joints):
        temp_joint = joint_list[i]
        cmds.parent(temp_joint, follicles_list[i])
        cmds.setAttr(temp_joint + '.translateX', 0)
        cmds.setAttr(temp_joint + '.translateY', 0)
        cmds.setAttr(temp_joint + '.translateZ', 0)
        cmds.rename(temp_joint, f'sk_joint_{ribbon_name}_0{i+1}')


    # Get the new joint names in a list
    joint_list = []
    for i in follicles_list:
        temp_joint = cmds.listRelatives(i, children=True, type='joint')
        temp_joint = temp_joint[0]
        joint_list.append(temp_joint)

    if cmds.checkBox('drivers_checkbox', q=1, v=1) == 1:
        # Create the controller joints by duplicating existing joints
        controller_joints = []
        counter = 1
        for i in range(number_of_controllers):
            controller_joints.append(f'sk_joint_{ribbon_name}_0{counter}')
            counter = counter + 4

        driver_joints = cmds.duplicate(controller_joints)
        cmds.parent(driver_joints, world=True)

        counter = 1
        for i in driver_joints:
            cmds.setAttr(i + '.radius', .5)
            cmds.rename(i, f'sk_{ribbon_name}_control_0{counter}')
            counter += 1

        driver_joints = []
        for i in range(number_of_controllers):
            driver_joints.append(f'sk_{ribbon_name}_control_0{i+1}')

        if cmds.objExists('grp_JNTS') is True:
            cmds.parent(driver_joints, 'grp_JNTS')
        else:
            cmds.group(driver_joints, name='grp_JNTS')

    if cmds.checkBox('ctrl_checkbox', q=1, v=1) == 1:
        # Create controllers and match them to their joint
        counter = 1
        controllers_list = []
        offsets_list = []
        for i in driver_joints:
            temp_ctrl = cmds.circle(nr=[0, 1, 0], n=f'ctrl_{ribbon_name}_control_0{counter}')

            temp_cstr = cmds.group(temp_ctrl, n=f'constrain_{ribbon_name}_control_0{counter}')
            temp_offset = cmds.group(temp_cstr, n=f'offset_{ribbon_name}_control_0{counter}')
            cmds.matchTransform(temp_offset, i)
            cmds.delete(temp_ctrl, constructionHistory=True)
            temp_ctrl = temp_ctrl[0]
            controllers_list.append(temp_ctrl)
            offsets_list.append(temp_offset)
            counter += 1

        if cmds.objExists('grp_CTRLS') is True:
            cmds.parent(offsets_list, 'grp_CTRLS')
        else:
            cmds.group(offsets_list, name='grp_CTRLS')


        #  Do the matrix constraints
        counter = 0
        for i in driver_joints:
            matrixConstraint(i, controllers_list[counter])
            counter += 1

    if cmds.checkBox('drivers_checkbox', q=1, v=1) == 1:
        # Bind driver joints to NURB Surface
        driver_joints.append(user_sel)
        cmds.skinCluster(driver_joints, bm=0, mi=5)

    # Rename NURB Surface
    cmds.rename(user_sel, f'nurb_{ribbon_name}')


# Define the point on surface function
def pointOnSurfaceRibbon():

    global number_of_controllers
    global controllers_list
    global ribbon_name

    # Handling text field variable3
    if len(cmds.textField('name_text_field', query=True, text=True)) == 0:
        ribbon_name = 'temp_ribbon'
    else:
        ribbon_name = cmds.textField('name_text_field', query=True, text=True)

    if len(cmds.textField('ctrls_text_field', query=True, text=True)) == 0:
        number_of_controllers = 5
    else:
        number_of_controllers = int(cmds.textField('ctrls_text_field', query=True, text=True))

    num_joints(number_of_controllers)
    selNurb()
    ribbonPrep(0)

    # Create joints and parent them
    joints_list = []
    groups_list = []
    driven_group = cmds.group(n=f'grp_{ribbon_name}_joints', empty=1)
    cmds.select(d=1)

    for i in range(number_of_joints):
        temp_joint = cmds.joint(radius=0.2, n=f'jnt_{ribbon_name}_0{i+1}')
        joints_list.append(temp_joint)
        cmds.select(d=1)
        offset_joint_grp = cmds.group(n=f'offset_jnt_{ribbon_name}_0{i+1}', p=driven_group, empty=1)
        cmds.parent(temp_joint, offset_joint_grp)
        groups_list.append(offset_joint_grp)
        cmds.select(d=1)

    if cmds.objExists('grp_JNTS') is True:
        cmds.parent(driven_group, 'grp_JNTS')
    else:
        cmds.group(driven_group, name='grp_JNTS')

    # Create nodes and make the connections for the POS

    # Get the shape of the NURB
    shape = cmds.listRelatives(user_sel)[0]

    counter = 0
    for i in groups_list:

        p_o_s = cmds.createNode('pointOnSurfaceInfo', n=f'{ribbon_name}_pos')
        four_by_four = cmds.createNode('fourByFourMatrix', n=f'{ribbon_name}_pos_ffm')
        mult = cmds.createNode('multMatrix', n=f'{ribbon_name}_pos_mm')
        decomp = cmds.createNode('decomposeMatrix', n=f'{ribbon_name}_pos_dcm')

        cmds.connectAttr(f'{shape}.worldSpace[0]', f'{p_o_s}.inputSurface')
        cmds.connectAttr(f'{p_o_s}.result.normalizedTangentU.normalizedTangentUX', f'{four_by_four}.in00')
        cmds.connectAttr(f'{p_o_s}.result.normalizedTangentU.normalizedTangentUY', f'{four_by_four}.in01')
        cmds.connectAttr(f'{p_o_s}.result.normalizedTangentU.normalizedTangentUZ', f'{four_by_four}.in02')
        cmds.connectAttr(f'{p_o_s}.result.normalizedTangentV.normalizedTangentVX', f'{four_by_four}.in10')
        cmds.connectAttr(f'{p_o_s}.result.normalizedTangentV.normalizedTangentVY', f'{four_by_four}.in11')
        cmds.connectAttr(f'{p_o_s}.result.normalizedTangentV.normalizedTangentVZ', f'{four_by_four}.in12')
        cmds.connectAttr(f'{p_o_s}.result.normalizedNormal.normalizedNormalX', f'{four_by_four}.in20')
        cmds.connectAttr(f'{p_o_s}.result.normalizedNormal.normalizedNormalY', f'{four_by_four}.in21')
        cmds.connectAttr(f'{p_o_s}.result.normalizedNormal.normalizedNormalZ', f'{four_by_four}.in22')
        cmds.connectAttr(f'{p_o_s}.result.position.positionX', f'{four_by_four}.in30')
        cmds.connectAttr(f'{p_o_s}.result.position.positionY', f'{four_by_four}.in31')
        cmds.connectAttr(f'{p_o_s}.result.position.positionZ', f'{four_by_four}.in32')

        cmds.connectAttr(f'{four_by_four}.output', f'{mult}.matrixIn[0]')
        cmds.connectAttr(f'{i}.parentInverseMatrix', f'{mult}.matrixIn[1]')
        cmds.connectAttr(f'{mult}.matrixSum', f'{decomp}.inputMatrix')
        cmds.connectAttr(f'{decomp}.outputRotate', f'{i}.rotate')
        cmds.connectAttr(f'{decomp}.outputTranslate', f'{i}.translate')

        # Change position of joint on ribbon
        cmds.setAttr(f'{p_o_s}.turnOnPercentage', 1)

        increment = 1 / (number_of_joints-1)

        if main_side == 'V':
            cmds.setAttr(f'{p_o_s}.parameterU', 0.5)
            cmds.setAttr(f'{p_o_s}.parameterV', increment*counter)
        if main_side == 'U':
            cmds.setAttr(f'{p_o_s}.parameterV', 0.5)
            cmds.setAttr(f'{p_o_s}.parameterU', increment*counter)

        # Add the counter joint orientation
        cmds.setAttr(f'{joints_list[counter]}.jointOrientX', 90)

        counter += 1

    if cmds.checkBox('drivers_checkbox', q=1, v=1) == 1:
        # Create the controller joints by duplicating existing joints
        driver_joints = []
        counter = 1
        for i in range(number_of_controllers):
            temp_joint = f'jnt_{ribbon_name}_0{counter}'
            position = cmds.xform(temp_joint, q=1, m=1, ws=1)

            new_joint = cmds.duplicate(temp_joint)
            new_joint = new_joint[0]
            driver_joints.append(new_joint)

            cmds.xform(new_joint, m=position, ws=1)
            cmds.setAttr(f'{new_joint}.rotateX', 0)
            cmds.setAttr(f'{new_joint}.rotateY', 0)
            cmds.setAttr(f'{new_joint}.rotateZ', 0)

            counter = counter + 4

        cmds.parent(driver_joints, world=True)

        counter = 1
        for i in driver_joints:
            cmds.setAttr(i + '.radius', .5)
            cmds.rename(i, f'sk_{ribbon_name}_control_0{counter}')
            counter += 1

        driver_joints = []
        for i in range(number_of_controllers):
            driver_joints.append(f'sk_{ribbon_name}_control_0{i+1}')

        if cmds.objExists('grp_JNTS') is True:
            cmds.parent(driver_joints, 'grp_JNTS')
        else:
            cmds.group(driver_joints, name='grp_JNTS')


    if cmds.checkBox('ctrl_checkbox', q=1, v=1) == 1:
        # Create controllers and match them to their joint
        counter = 1
        controllers_list = []
        offsets_list = []
        for i in driver_joints:
            temp_ctrl = cmds.circle(nr=[0, 1, 0], n=f'ctrl_{ribbon_name}_control_0{counter}')

            temp_cstr = cmds.group(temp_ctrl, n=f'constrain_{ribbon_name}_control_0{counter}')
            temp_offset = cmds.group(temp_cstr, n=f'offset_{ribbon_name}_control_0{counter}')
            cmds.matchTransform(temp_offset, i)
            cmds.delete(temp_ctrl, constructionHistory=True)
            temp_ctrl = temp_ctrl[0]
            controllers_list.append(temp_ctrl)
            offsets_list.append(temp_offset)
            counter += 1

        if cmds.objExists('grp_CTRLS') is True:
            cmds.parent(offsets_list, 'grp_CTRLS')
        else:
            cmds.group(offsets_list, name='grp_CTRLS')


        #  Do the matrix constraints
        counter = 0
        for i in driver_joints:
            matrixConstraint(i, controllers_list[counter])
            counter += 1

    if cmds.checkBox('drivers_checkbox', q=1, v=1) == 1:
        # Bind driver joints to NURB Surface
        driver_joints.append(user_sel)
        cmds.skinCluster(driver_joints, bm=0, mi=5)

    # Rename NURB Surface
    cmds.rename(user_sel, f'nurb_{ribbon_name}')


# Controller function
def runScript(*args):

    if cmds.optionMenu('ribbon_type_menu', q=1, v=1) == 'Point On Surface':
        pointOnSurfaceRibbon()
    else:
        folliclesRibbon()


# UI launcher
def ribbonAutomationUI():

    # Check if window already exists and deletes it
    if cmds.window('ribbonAutomationUI', ex=True):
        cmds.deleteUI('ribbonAutomationUI')

    # Create window
    window = cmds.window('ribbonAutomationUI', title='Ribbon Builder v3.0', w=220, h=260,
                         mnb=False, mxb=False, sizeable=False)

    # Create main Layout
    main_layout = cmds.formLayout(nd=100)

    # Create Title
    title = cmds.text(label='Ribbon Builder', font='boldLabelFont')

    # Create Separators
    separator_01 = cmds.separator(h=5, style='shelf')
    separator_02 = cmds.separator(h=5, style='shelf')

    # Create number of controllers writing field
    ctrls_text_field = cmds.textField('ctrls_text_field', pht = '5', w=75)

    # Create ribbon name writing field
    name_text_field = cmds.textField('name_text_field', pht = 'temp_ribbon', w=110)

    # Create ribbon type menu
    type_menu = cmds.optionMenu('ribbon_type_menu', label='Ribbon Type', h=20,
                                ann='What type of ribbon do you want to create?')
    cmds.menuItem(label='Point On Surface')
    cmds.menuItem(label='Follicles')

    # Create controllers checkbox
    ctrl_checkbox = cmds.checkBox('ctrl_checkbox', label='Controllers', value=1, onCommand=driversCheckboxOn, offCommand=driversCheckboxOff)

    # Create driver joints checkbox
    drivers_checkbox = cmds.checkBox('drivers_checkbox', label='Driver Joints', value=1, ed=0)

    # Create button
    button = cmds.button(label='CREATE', ann='Create The Ribbon', command=runScript)

    # Create Missing Titles
    ctrls_title = cmds.text(label='Number of Controllers', ann='number of spans/2 + 1')
    name_title = cmds.text(label='Ribbon Name')

    # Adjust layout
    cmds.formLayout(main_layout, e=True,
                    attachForm = [(title, 'top', 7), (title, 'left', 5), (title, 'right', 5),

                                  (separator_01, 'left', 5), (separator_01, 'right', 5),

                                  (separator_02, 'left', 5), (separator_02, 'right', 5),

                                  (ctrls_text_field, 'left', 128),

                                  (name_text_field, 'left', 92),

                                  (ctrls_title, 'left', 5),

                                  (name_title, 'left', 10),

                                  (type_menu, 'left', 7),

                                  (ctrl_checkbox, 'left', 25), (drivers_checkbox, 'left', 115),

                                  (button, 'left', 5), (button, 'right', 5), (button, 'bottom', 5)
                    ],

                    attachControl = [(separator_01, 'top', 5, title),

                                     (ctrls_text_field, 'top', 15, separator_01),

                                     (ctrls_title, 'top', 15, separator_01),

                                     (name_text_field, 'top', 10, ctrls_text_field),

                                     (name_title, 'top', 10, ctrls_text_field),

                                     (separator_02, 'top', 15, name_text_field),

                                     (type_menu, 'top', 15, separator_02),

                                     (ctrl_checkbox, 'top', 10, type_menu),

                                     (drivers_checkbox, 'top', 10, type_menu),

                                     (button, 'top', 12, ctrl_checkbox)
                    ]
                    )


    # Show the window
    cmds.showWindow(window)


ribbonAutomationUI()
