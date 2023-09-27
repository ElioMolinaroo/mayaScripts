import maya.cmds as cmds
import maya.mel as mm

sel_jnt = cmds.ls(sl=1)[0]

skin_cluster = cmds.listConnections(sel_jnt, type="skinCluster")[0]

mesh = cmds.listConnections(skin_cluster, type="mesh")[0]

vtx_sel = mm.eval(f'skinCluster -e -selectInfluenceVerts {sel_jnt} {skin_cluster};')

cmds.selectMode(co=1)
