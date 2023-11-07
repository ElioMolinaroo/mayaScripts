#------------------------------------------------------------------------------------------
#
#-------------  Matrix Constraint Automation Script v2.7 by Elio Molinaro  ----------------
#
#------------------------------------------------------------------------------------------

"""UI to create matrix constraints with multiple options"""

import maya.cmds as cmds


# UI checkbox changes
def parentOn(*args):
    cmds.checkBox('point', edit=True, value=0)
    cmds.checkBox('orient', edit=True, value=0)
def pointOn(*args):
    cmds.checkBox('parent', edit=True, value=0)
    cmds.checkBox('orient', edit=True, value=0)
def orientOn(*args):
    cmds.checkBox('point', edit=True, value=0)
    cmds.checkBox('parent', edit=True, value=0)


# Constraints Creator
def matrixConstraint(*args):

    global constraint_type

    # Create created objects list
    created_objects = []

    # Get user selection
    sel = cmds.ls(sl=True)

    # Handling UI variables
    if cmds.optionMenu('mode_menu', q=True, v=True) == 'Single':
        simple_constraint_check = True
    else:
        simple_constraint_check = False

    if cmds.checkBox('control_checkbox', q=True, v=True) is True:
        create_controller = True
        if len(sel) > 1:
            cmds.error('Uncheck create controller if you want to use your own')
    else:
        create_controller = False

    if cmds.checkBox('maintain_offset_checkbox', q=True, v=True) is True:
        maintain_offset = True
    else:
        maintain_offset = False

    # Controller creation
    if create_controller and simple_constraint_check is True:
        sel = cmds.ls(sl=True)
        controller = cmds.circle(nr=[0, 1, 0], n='ctrl_tempName')
        controller = controller[0]
        created_objects.append(controller)

        cmds.delete(controller, constructionHistory=True)
        offset_group = cmds.group(controller, n='offset_tempName')
        cmds.matchTransform(offset_group, sel)
        created_objects.append(offset_group)

        sel.append(controller)
    elif create_controller is True and simple_constraint_check is False:
        cmds.delete(created_objects)
        cmds.error("Cannot create controller with Constraint Type set to 'Multiple'")
    else:
        pass

    # Splitting parent and child selection
    if simple_constraint_check is True:
        if len(sel) != 2:
            cmds.delete(created_objects)
            cmds.error('Please select 2 objects or switch to Multiple Constraints')
        else:
            pass

        parent = sel[len(sel) - 1]
        sel.remove(parent)
        child = sel

    elif simple_constraint_check is False:
        child = sel[0]
        sel.remove(child)
        parents_list = sel

    if simple_constraint_check is True:
        child = child[0]
    else:
        pass

    '''# Check if child object(s) has a parent + stores that parent into a variable
    if cmds.listRelatives(child, p=True) is None:
        cmds.delete(created_objects)
        cmds.error(f"Child object '{child}' needs to have a parent")
    else:
        child_parent = cmds.listRelatives(child, p=True)
        child_parent = child_parent[0]'''

    # Check if child is a joint
    if cmds.nodeType(child) == 'joint':
        is_child_joint = True
    else:
        is_child_joint = False

    # Check type of constraint
    if cmds.checkBox('parent', query=True, value=True) == 1:
        constraint_type = 'parent'
    elif cmds.checkBox('point', query=True, value=True) == 1:
        constraint_type = 'point'
    elif cmds.checkBox('orient', query=True, value=True) == 1:
        constraint_type = 'orient'
    else:
        cmds.error('Please select a constraint type')

    # Create simple constraint function
    def simpleConstraint():

        if maintain_offset is True:
            proxy_attr = cmds.addAttr(parent, sn='proxyAttr', dt='matrix')

        # create nodes
        if maintain_offset is True:
            mult_matrix_maintain = cmds.createNode('multMatrix', n=f'{child}_maintain_util_mm')
            created_objects.append(mult_matrix_maintain)

        mult_matrix = cmds.createNode('multMatrix', n=f'{child}_util_mm')
        decompose_matrix = cmds.createNode('decomposeMatrix', n=f'{child}_util_dcm')
        created_objects.append(mult_matrix)
        created_objects.append(decompose_matrix)

        # Make connections
        if maintain_offset is True:
            cmds.connectAttr(f'{child}.worldMatrix[0]', f'{mult_matrix_maintain}.matrixIn[0]')
            cmds.connectAttr(f'{parent}.worldInverseMatrix[0]', f'{mult_matrix_maintain}.matrixIn[1]')
            cmds.connectAttr(f'{mult_matrix_maintain}.matrixSum', f'{parent}.proxyAttr')
            cmds.disconnectAttr(f'{mult_matrix_maintain}.matrixSum', f'{parent}.proxyAttr')
            cmds.connectAttr(f'{parent}.proxyAttr', f'{mult_matrix}.matrixIn[0]')
            cmds.connectAttr(f'{parent}.worldMatrix[0]', f'{mult_matrix}.matrixIn[1]')
            cmds.connectAttr(f'{child}.parentInverseMatrix[0]', f'{mult_matrix}.matrixIn[2]')
            cmds.connectAttr(f'{mult_matrix}.matrixSum', f'{decompose_matrix}.inputMatrix')
            cmds.delete(mult_matrix_maintain)
        elif maintain_offset is False:
            cmds.connectAttr(f'{parent}.worldMatrix[0]', f'{mult_matrix}.matrixIn[0]')
            cmds.connectAttr(f'{child}.parentInverseMatrix[0]', f'{mult_matrix}.matrixIn[1]')
            cmds.connectAttr(f'{mult_matrix}.matrixSum', f'{decompose_matrix}.inputMatrix')

        if constraint_type == 'parent':
            cmds.connectAttr(f'{decompose_matrix}.outputTranslate', f'{child}.translate')
            cmds.connectAttr(f'{decompose_matrix}.outputRotate', f'{child}.rotate')
            cmds.connectAttr(f'{decompose_matrix}.outputScale', f'{child}.scale')

        elif constraint_type == 'point':
            cmds.connectAttr(f'{decompose_matrix}.outputTranslate', f'{child}.translate')

        elif constraint_type == 'orient':
            cmds.connectAttr(f'{decompose_matrix}.outputRotate', f'{child}.rotate')

        # Reset joint orientation if type = joint
        if is_child_joint is True:
            cmds.setAttr(f'{child}.jointOrientX', 0)
            cmds.setAttr(f'{child}.jointOrientY', 0)
            cmds.setAttr(f'{child}.jointOrientZ', 0)
        else:
            pass

    # Create multiple constraint function
    def multipleConstraint():

        # create shared nodes
        decompose_matrix = cmds.createNode('decomposeMatrix', f'{child}_util_dcm')
        blend_matrix = cmds.createNode('blendMatrix', n=f'{child}_util_blm')
        created_objects.append(decompose_matrix)
        created_objects.append(blend_matrix)

        # Create iteration nodes + make their connections
        for i in range(len(parents_list)):
            mult_matrix = cmds.createNode('multMatrix', n=f'{child}_util_mm{i+1}')
            created_objects.append(mult_matrix)

            current_parent = parents_list[i]

            cmds.connectAttr(f'{current_parent}.worldMatrix[0]', f'{mult_matrix}.matrixIn[0]')
            cmds.connectAttr(f'{child}.parentInverseMatrix[0]', f'{mult_matrix}.matrixIn[1]')

        cmds.connectAttr(f'{child}_mm_1.matrixSum', f'{blend_matrix}.inputMatrix')

        for i in range(len(parents_list)-1):
            current_parent = parents_list[i+1]

            cmds.connectAttr(f'{child}_mm_{i+2}.matrixSum', f'{blend_matrix}.target[{i}].targetMatrix')

        # create shared connexions
        cmds.connectAttr(f'{blend_matrix}.outputMatrix', f'{decompose_matrix}.inputMatrix')

        if constraint_type == 'parent':
            cmds.connectAttr(f'{decompose_matrix}.outputTranslate', f'{child}.translate')
            cmds.connectAttr(f'{decompose_matrix}.outputRotate', f'{child}.rotate')
            cmds.connectAttr(f'{decompose_matrix}.outputScale', f'{child}.scale')

        elif constraint_type == 'point':
            cmds.connectAttr(f'{decompose_matrix}.outputTranslate', f'{child}.translate')

        elif constraint_type == 'orient':
            cmds.connectAttr(f'{decompose_matrix}.outputRotate', f'{child}.rotate')

        # Reset joint orientation if type = joint
        if is_child_joint is True:
            cmds.setAttr(f'{child}.jointOrientX', 0)
            cmds.setAttr(f'{child}.jointOrientY', 0)
            cmds.setAttr(f'{child}.jointOrientZ', 0)
        else:
            pass

    # Runs the appropriate function
    if simple_constraint_check is True:
        simpleConstraint()

    else:
        multipleConstraint()


# Delete Constraints
def deleteConstraints(*args):

    # Get User Selection
    sel = cmds.ls(sl=True)

    for i in sel:
        connection_1 = cmds.listConnections(i)

        temp1 = cmds.listConnections(i, source=True)[0]
        temp2 = cmds.listConnections(temp1, source=True)[0]
        ctrl = cmds.listConnections(temp2, source=True)[0]

        if connection_1 != None:
            for j in connection_1:
                if '_dcm' in j:
                    connection_1 = j
                    break

            if '_dcm' in connection_1:
                connection_2 = cmds.listConnections(connection_1)
                for k in connection_2:
                    if '_mm' in k:
                        connection_2 = k
                        break

                cmds.delete(connection_1, connection_2)

        attrs = cmds.listAttr(ctrl)
        for i in attrs:
            if i == 'proxyAttr':
                proxy_attr = i
                break
            else:
                proxy_attr = 0

        if proxy_attr != 0:
            cmds.deleteAttr(f'{ctrl}.{proxy_attr}')
        else:
            pass


# Replace parent constraints by matrix ones
def parentReplace(*args):

    constr = cmds.ls(sl=True)
    if constr == []:
        cmds.error('Please select a parent constraint')

    for i in constr:
        child = cmds.listRelatives(i, parent=True)[0]
        parent = cmds.parentConstraint(i, q=True, tl=True)[0]

        # Check if child object(s) has a parent + stores that parent into a variable
        if cmds.listRelatives(child, p=True) is None:
            cmds.error(f"Child object '{child}' needs to have a parent")
        else:
            child_parent = cmds.listRelatives(child, p=True)
            child_parent = child_parent[0]

        cmds.delete(i)

        cmds.select(child, parent)

        cmds.checkBox('control_checkbox', edit=True, value=0)

        matrixConstraint()


# Add proxy matrix attribute to selection
def addProxyAttr(*args):

    sel = cmds.ls(sl=1)

    for i in sel:
        cmds.addAttr(i, dt='matrix', ln='proxyAttr', nn='Proxy Attr')


# Create UI
def matrixConstraintUI():

    global parent
    global point
    global orient

    # Check if window already exists and deletes it
    if cmds.window('matrixConstraintUI', ex=True):
        cmds.deleteUI('matrixConstraintUI')

    # Create window
    window = cmds.window('matrixConstraintUI', title='Matrix Constraint Tool v2.7', w=240, h=330,
                         mnb=False, mxb=False, sizeable=False)

    # Create main Layout
    main_layout = cmds.formLayout(nd=100)

    # Create Title
    title = cmds.text(label='Matrix Constraint Tool', font='boldLabelFont')

    # Create control checkbox
    control_checkbox = cmds.checkBox('control_checkbox', label='Create Controller',
                                     ann='Do you already have a controller or do you want to create one?', h=20)

    # Create maintain offset checkbox
    maintain_offset_checkbox = cmds.checkBox('maintain_offset_checkbox', label='Maintain Offset',
                                     ann='Do you want to maintain the offset?', h=20)

    # Create Menu
    mode_menu = cmds.optionMenu('mode_menu', label='Constraint Mode', h=20,
                                ann='Do you want to constrain a single child or multiple children?')

    cmds.menuItem(label='Single')
    cmds.menuItem(label='Multiple')

    # Create Constraint Type Checkboxes
    parent = cmds.checkBox('parent', label='Parent', value=1, onCommand=parentOn,
                           ann='What type of constraint do you want?')
    point = cmds.checkBox('point', label='Point', onCommand=pointOn,
                          ann='What type of constraint do you want?')
    orient = cmds.checkBox('orient', label='Orient', onCommand=orientOn,
                           ann='What type of constraint do you want?')

    # Create Separators
    separator_01 = cmds.separator(h=5, style='shelf')
    separator_02 = cmds.separator(h=5, style='none')
    separator_03 = cmds.separator(h=5, style='none')

    # Create the Create Button
    create_button = cmds.button(label='CREATE', command=matrixConstraint, ann='Create the constraint (selection order: child then parent)')

    # Create the Delete Button
    delete_button = cmds.button(label='DELETE', command=deleteConstraints,
                                ann='Select a constrained object to delete its constraint')

    # Create the Parent Replace Button
    replace_button = cmds.button(label='REPLACE P.C', command=parentReplace, ann='Select a parentConstraint node to replace a parent constraint by a matrix constraint')

    # Create the Create Proxy Attr Button
    proxy_attr_button = cmds.button(label='CREATE PROXY ATTR', command=addProxyAttr, ann='Create matrix proxy attribute on the selected objects')

    # Adjust Layout
    cmds.formLayout(main_layout, e=True,
                    attachForm = [(title, 'top', 10), (title, 'left', 5), (title, 'right', 5),

                                  (separator_01, 'left', 5), (separator_01, 'right', 5),

                                  (separator_02, 'left', 5), (separator_02, 'right', 5),

                                  (mode_menu, 'left', 30), (mode_menu, 'right', 30),

                                  (separator_03, 'left', 5), (separator_03, 'right', 5),

                                  (parent, 'left', 30), (point, 'left', 95), (orient, 'left', 155),

                                  (create_button, 'left', 5), (create_button, 'right', 5),

                                  (delete_button, 'left', 5), (delete_button, 'right', 5),

                                  (replace_button, 'left', 5), (replace_button, 'right', 5),

                                  (proxy_attr_button, 'bottom', 7), (proxy_attr_button, 'left', 5), (proxy_attr_button, 'right', 5)
                    ],

                    attachControl = [(separator_01, 'top', 10, title),

                                     (control_checkbox, 'top', 10, separator_01),

                                     (separator_02, 'top', 0, control_checkbox),

                                     (maintain_offset_checkbox, 'top', 10, separator_01),

                                     (separator_02, 'top', 0, maintain_offset_checkbox),

                                     (mode_menu, 'top', 10, separator_02),

                                     (parent, 'top', 15, mode_menu),

                                     (point, 'top', 15, mode_menu),

                                     (orient, 'top', 15, mode_menu),

                                     (create_button, 'top', 20, parent),

                                     (create_button, 'bottom', 10, delete_button),

                                     (delete_button, 'bottom', 10, replace_button),

                                     (replace_button, 'bottom', 10, proxy_attr_button)
                    ],
                    attachPosition = [(control_checkbox, 'left', 0, 5),
                                      (maintain_offset_checkbox, 'left', 0, 53)
                    ]
                    )

    # Show the window
    cmds.showWindow(window)


matrixConstraintUI()
