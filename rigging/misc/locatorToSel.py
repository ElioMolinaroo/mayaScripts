"""Create locators and snaps them to the selected items"""

import maya.cmds as cmds

sel = cmds.ls(sl=1)

for i in sel:
    loc = cmds.spaceLocator(p=(0, 0, 0))
    cmds.matchTransform(loc, i)
    