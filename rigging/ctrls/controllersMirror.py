import maya.cmds as cmds


# UI checkbox changes
def xOn(*args):
    cmds.checkBox('y', edit=True, value=0)
    cmds.checkBox('z', edit=True, value=0)
def yOn(*args):
    cmds.checkBox('x', edit=True, value=0)
    cmds.checkBox('z', edit=True, value=0)
def zOn(*args):
    cmds.checkBox('x', edit=True, value=0)
    cmds.checkBox('y', edit=True, value=0)


def switchSign(number):
    if number > 0:
        number = -abs(number)
    elif number < 0:
        number = abs(number)
    return number


def mirrorControllers(*args):

    sel = cmds.ls(sl=1)

    for i in sel:
        trs = cmds.xform(i, q=1, t=1, ws=1)
        rot = cmds.xform(i, q=1, ro=1, ws=1)

        if cmds.checkBox(x_axis, q=1, v=1) == 1:
            mirror_trs = [switchSign(trs[0]), trs[1], trs[2]]
            mirror_rot = [rot[0], switchSign(rot[1]), switchSign(rot[2])]
        elif cmds.checkBox(y_axis, q=1, v=1) == 1:
            mirror_trs = [trs[0], switchSign(trs[1]), trs[2]]
            mirror_rot = [switchSign(rot[0]), rot[1], switchSign(rot[2])]
        elif cmds.checkBox(z_axis, q=1, v=1) == 1:
            mirror_trs = [trs[0], trs[1], switchSign(trs[2])]
            mirror_rot = [switchSign(rot[0]), switchSign(rot[1]), rot[2]]

        parent = cmds.listRelatives(i, p=1)[0]

        if '_L' in parent:
            parent_mirrored_name = parent.replace('_L', '_R')
            ctrl_mirrored_name = i.replace('_L', '_R')
            colour = 18

        elif '_R' in parent:
            parent_mirrored_name = parent.replace('_R', '_L')
            ctrl_mirrored_name = i.replace('_R', '_L')
            colour = 13

        mirror = cmds.duplicate(parent, n= parent_mirrored_name, rc=1)
        mirror_child = cmds.listRelatives(mirror, c=1)[0]
        mirror_child = cmds.rename(mirror_child, ctrl_mirrored_name)
        mirror = cmds.listRelatives(mirror_child, p=1)[0]

        cmds.xform(mirror, t=mirror_trs, ro=mirror_rot, ws=1)

        if cmds.checkBox(update_colour, q=1, v=1) == 1:
            mirror_child_shape = cmds.listRelatives(mirror_child, s=1)[0]
            cmds.setAttr(f'{mirror_child_shape}.overrideColor', colour)

        if cmds.objExists('grp_CTRLS') is True:
            cmds.parent(mirror, 'grp_CTRLS')
        else:
            cmds.group(mirror, name='grp_CTRLS')


# Create UI
def mirrorControllersUI():

    global x_axis
    global y_axis
    global z_axis
    global update_colour

    # Check if window already exists and deletes it
    if cmds.window('mirrorControllersUI', ex=True):
        cmds.deleteUI('mirrorControllersUI')

    # Create window
    window = cmds.window('mirrorControllersUI', title='Mirror Controllers v1.0', w=200, h=200,
                         mnb=False, mxb=False, sizeable=False)

    # Create main Layout
    main_layout = cmds.formLayout(nd=100)

    # Create Title
    title = cmds.text(label='Mirror Controllers Tool', font='boldLabelFont')

    # Create Mirror Axis Checkboxes
    x_axis = cmds.checkBox('x', label='X', value=1, onCommand=xOn,
                           ann='What axis do you want to mirror the controllers on?')
    y_axis = cmds.checkBox('y', label='Y', onCommand=yOn,
                           ann='What axis do you want to mirror the controllers on?')
    z_axis = cmds.checkBox('z', label='Z', onCommand=zOn,
                           ann='What axis do you want to mirror the controllers on?')

    # Create Colour Update Checkbox
    update_colour = cmds.checkBox('update_colour', label='Update Colour', value=0,
                                  ann='Do you want to update the colour to reflect the change in character side?')

    # Create Separators
    separator_01 = cmds.separator(h=5, style='shelf')

    # Create the Create Button
    create_button = cmds.button(label='MIRROR', command=mirrorControllers, ann='Mirrors the selected controllers')

    # Adjust Layout
    cmds.formLayout(main_layout, e=True,
                    attachForm = [(title, 'top', 10), (title, 'left', 5), (title, 'right', 5),
                                  (update_colour, 'left', 55),
                                  (create_button, 'bottom', 5), (create_button, 'left', 5), (create_button, 'right', 5),
                                  (x_axis, 'left', 35),
                                  (y_axis, 'left', 90),
                                  (z_axis, 'left', 140),
                                  ],

                    attachControl = [(separator_01, 'top', 5, title),
                                     (x_axis, 'top', 10, separator_01),
                                     (y_axis, 'top', 10, separator_01),
                                     (z_axis, 'top', 10, separator_01),
                                     (update_colour, 'top', 15, x_axis),
                                     (create_button, 'top', 20, update_colour)
                                     ]
                    )

    # Show the window
    cmds.showWindow(window)


mirrorControllersUI()
