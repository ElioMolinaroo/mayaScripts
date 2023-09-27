#------------------------------------------------------------------------------------------
#
#---------------  Quick Attribute Separator Script v1.0 by Elio Molinaro  -----------------
#
#------------------------------------------------------------------------------------------

import maya.cmds as cmds


# Main Function
def quickAttribute(separator_name):

    # Get user selection
    controller = cmds.ls(sl=1)

    if len(controller) != 1:
        cmds.error('Please select only one controller')
    else:
        controller = controller[0]

    # Create the attribute
    long_name = separator_name.replace(' ', '_')
    attribute = cmds.addAttr(controller, at='enum', ln=long_name, nn=f'____{separator_name}____', enumName='____________')
    cmds.setAttr(f'{controller}.{long_name}', cb=1)


# Create UI
def quickAttributeUI():

    global separator_name

    result = cmds.promptDialog(
        title='Quick Attribute Separator',
        message='Separator Name:',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel')

    if result == 'OK':
        separator_name = cmds.promptDialog(query=True, text=True)

        quickAttribute(separator_name)


quickAttributeUI()
