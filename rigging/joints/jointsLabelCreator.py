import maya.cmds as cmds

sel = cmds.ls(sl=1)

for i in sel:
    cmds.setAttr(f'{i}.type', 18)

    joint_label = i

    if '_L' in i:
        cmds.setAttr(f'{i}.side', 1)
        joint_label = joint_label.replace('_L', '')
    elif '_R' in i:
        cmds.setAttr(f'{i}.side', 2)
        joint_label = joint_label.replace('_R', '')
    else:
        cmds.setAttr(f'{i}.side', 0)

    cmds.setAttr(f'{i}.otherType', joint_label, type='string')
    