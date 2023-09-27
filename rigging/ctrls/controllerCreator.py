#------------------------------------------------------------------------------------------
#
#------------------  Controller Creation Script v1.7 by Elio Molinaro  --------------------
#
#------------------------------------------------------------------------------------------

import maya.cmds as cmds
import pymel.core as pm

# Setting Constants
GREY = 3
BLACK = 2
BLUE = 7
MAGENTA = 10
RED = 14
GREEN = 15
WHITE = 16
YELLOW = 18
TURQUOISE = 19

TRIANGLE_POINTS = 'curve -d 1 -p -0.681886 0 -1.241162 -p 1.318114 0 0 -p -0.681886 0 1.241162 -p -0.681886 0 -1.241162 -k 0 -k 1 -k 2 -k 3 ;'
CUBE_POINTS = 'curve -d 1 -p 1 1 1 -p -1 1 1 -p -1 1 -1 -p 1 1 -1 -p 1 1 1 -p 1 -1 1 -p 1 -1 -1 -p 1 1 -1 -p -1 1 -1 -p -1 -1 -1 -p -1 -1 1 -p -1 1 1 -p -1 -1 1 -p 1 -1 1 -p 1 -1 -1 -p -1 -1 -1 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 ;'
CROSS_POINTS = 'curve -d 1 -p -0.414 0 0.414 -p -1.242 0 0.414 -p -1.242 0 -0.414 -p -0.414 0 -0.414 -p -0.414 0 -1.242 -p 0.414 0 -1.242 -p 0.414 0 -0.414 -p 1.242 0 -0.414 -p 1.242 0 0.414 -p 0.414 0 0.414 -p 0.414 0 1.242 -p -0.414 0 1.242 -p -0.414 0 0.414 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 ;'
ROTATE_POINTS = 'curve -d 1 -p 0 0 -1.17 -p 0 0 -1.56 -p 0.399338 0 -1.506031 -p 0.793524 0 -1.338937 -p 1.103095 0 -1.103096 -p 1.345836 0 -0.784469 -p 1.499466 0 -0.417871 -p 1.560012 0 0 -p 1.506349 0 0.396973 -p 1.350447 0 0.777635 -p 1.103095 0 1.103095 -p 0.787278 0 1.343696 -p 0.403326 0 1.505491 -p 0.00914653 0 1.558776 -p -0.397476 0 1.506282 -p -0.771739 0 1.352889 -p -1.102027 0 1.103909 -p -1.349955 0 0.778822 -p -1.504247 0 0.406328 -p -1.560012 0 0 -p -1.972908 0 0 -p -1.357046 0 -1.231723 -p -0.741184 0 0 -p -1.170009 0 0 -p -1.1249 0 0.312677 -p -1.0035 0 0.596066 -p -0.829628 0 0.824294 -p -0.592335 0 1.006342 -p -0.321045 0 1.121435 -p 0.00996931 0 1.168661 -p 0.31291 0 1.124804 -p 0.584563 0 1.012264 -p 0.827321 0 0.827321 -p 1.014637 0 0.578876 -p 1.130714 0 0.290688 -p 1.169318 0 -0.00511019 -p 1.129118 0 -0.302495 -p 1.012303 0 -0.584511 -p 0.816803 0 -0.835335 -p 0.585095 0 -1.011857 -p 0.309292 0 -1.126304 -p 0 0 -1.17 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 -k 18 -k 19 -k 20 -k 21 -k 22 -k 23 -k 24 -k 25 -k 26 -k 27 -k 28 -k 29 -k 30 -k 31 -k 32 -k 33 -k 34 -k 35 -k 36 -k 37 -k 38 -k 39 -k 40 -k 41 ;'
SQUARE_POINTS = 'curve -d 1 -p 1 0 -1 -p 1 0 1 -p -1 0 1 -p -1 0 -1 -p 1 0 -1 -k 0 -k 1 -k 2 -k 3 -k 4 ;'
POLE_POINTS = 'curve -d 1 -p 0.622376 -0.656174 0.622376 -p 0.622376 -0.656174 -0.622376 -p -0.622376 -0.656174 -0.622376 -p -0.622376 -0.656174 0.622376 -p 0.622376 -0.656174 0.622376 -p 0 1.112776 0 -p -0.622376 -0.656174 0.622376 -p -0.622376 -0.656174 -0.622376 -p 0 1.112776 0 -p 0.622376 -0.656174 -0.622376 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 ;'
ARROW_POINTS = 'curve -d 1 -p -0.5214 0 0.5214 -p -1.056 0 0.363 -p -0.99 0 0.66 -p -1.65 0 0 -p -0.99 0 -0.66 -p -1.056 0 -0.363 -p -0.5214 0 -0.5214 -p -0.363 0 -1.056 -p -0.66 0 -0.99 -p 0 0 -1.65 -p 0.66 0 -0.99 -p 0.363 0 -1.056 -p 0.5214 0 -0.5214 -p 1.056 0 -0.363 -p 0.99 0 -0.66 -p 1.65 0 0 -p 0.99 0 0.66 -p 1.056 0 0.363 -p 0.5214 0 0.5214 -p 0.363 0 1.056 -p 0.66 0 0.99 -p 0 0 1.65 -p -0.66 0 0.99 -p -0.363 0 1.056 -p -0.5214 0 0.5214 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 -k 18 -k 19 -k 20 -k 21 -k 22 -k 23 -k 24 ;'


# Setting Variables
button = False


# -------------------------------------------------------------------------------------------------------
# Main Functions

def colourChange():

    # Get user selection
    user_sel = cmds.ls(sl=True)
    if len(user_sel) != 0:
        user_sel_shapes = cmds.listRelatives(user_sel, shapes=True)

        if user_sel_shapes is None:
            pass
        else:
            for i in user_sel_shapes:
                colour_value = cmds.colorIndexSliderGrp(colour_slider, query=True, value=True) - 1
                cmds.setAttr(i + '.overrideEnabled', 1)
                cmds.setAttr(i + '.overrideColor', colour_value)
    else:
        pass


def thicknessChange(*args):

    # Get user selection
    user_sel = cmds.ls(sl=True)
    if len(user_sel) != 0:
        user_sel_shapes = cmds.listRelatives(user_sel, shapes=True)
        if user_sel_shapes is None:
            pass
        else:
            if cmds.nodeType(user_sel_shapes[0]) == 'nurbsCurve':
                for i in user_sel_shapes:
                    thickness_value = cmds.floatSlider(thickness_slider, query=True, value=True)
                    cmds.setAttr(i + '.lineWidth', thickness_value)


def scaleChange(*args):

    global user_sel

    # Get user selection
    user_sel = cmds.ls(sl=True)
    user_sel_shapes = cmds.listRelatives(shapes=True)

    if user_sel_shapes is None:
        pass
    else:
        for i in user_sel_shapes:
            if cmds.nodeType(i) != 'nurbsCurve':
                cmds.error('Please only select NURBS curves')
        else:
            pass

        scale_value = cmds.floatSlider(scale_slider, query=True, value=True)
        cmds.scale(scale_value, scale_value, scale_value)


def deleteHistory(*args):

    global user_sel

    for i in user_sel:
        cmds.makeIdentity(i, apply=True, scale=1)
        cmds.delete(i, ch=True)


def createControl(*args):

    # Check if selection is empty
    user_sel = cmds.ls(sl=True)

    if len(user_sel) == 0:
        selection_empty = True
    elif len(user_sel) != 1:
        cmds.error('Please select only one object to match the controller to')
    else:
        selection_empty = False


    # Handling menu variable
    if cmds.optionMenu('style_menu', q=True, v=True) == 'Cube':
        control_type = CUBE_POINTS
    elif cmds.optionMenu('style_menu', q=True, v=True) == 'Arrow':
        control_type = ARROW_POINTS
    elif cmds.optionMenu('style_menu', q=True, v=True) == 'Pole':
        control_type = POLE_POINTS
    elif cmds.optionMenu('style_menu', q=True, v=True) == 'Square':
        control_type = SQUARE_POINTS
    elif cmds.optionMenu('style_menu', q=True, v=True) == 'Triangle':
        control_type = TRIANGLE_POINTS
    elif cmds.optionMenu('style_menu', q=True, v=True) == 'Rotate':
        control_type = ROTATE_POINTS
    elif cmds.optionMenu('style_menu', q=True, v=True) == 'Cross':
        control_type = CROSS_POINTS


    # Handling text field variable
    if len(cmds.textField(text_field, query=True, text=True)) == 0:
        control_name = 'tempName'
    else:
        control_name = cmds.textField(text_field, query=True, text=True)


    # Create controllers
    if cmds.optionMenu('style_menu', q=True, v=True) == 'Circle':
        control = cmds.circle(name='ctrl_' + control_name, normal=[0, 1, 0])[0]
        cmds.delete(control, ch=1)
    elif cmds.optionMenu('style_menu', q=True, v=True) == 'Pin':
        control = cmds.circle(name='ctrl_' + control_name, normal=[0, 1, 0])[0]
        base_shape = cmds.listRelatives(control, s=1)[0]
        line = pm.language.Mel.eval('curve -d 3 -p 0 0 1 -p 0 0 1.997968 -p 0 0 2.995935 -p 0 0 3.993903 -k 0 -k 0 -k 0 -k 1 -k 1 -k 1 ;')
        line_shape = cmds.listRelatives(line, s=1)[0]
        line_shape = cmds.rename(line_shape, base_shape+'1')
        cmds.parent(line_shape, control, r=1, s=1)
        cmds.delete(line)
        cmds.setAttr(f'{control}.translateZ', -4)
        cmds.select(control)
        pm.language.Mel.eval(f'move -rpr 0 0 -0.00609708 ctrl_{control_name}.scalePivot ctrl_{control_name}.rotatePivot ;')
        cmds.setAttr(f'{control}.rotateX', 90)
        cmds.setAttr(f'{control}.scaleX', 0.5)
        cmds.setAttr(f'{control}.scaleY', 0.5)
        cmds.setAttr(f'{control}.scaleZ', 0.5)
        cmds.makeIdentity(control, a=1)
        cmds.delete(control, ch=1)
    else:
        control = pm.language.Mel.eval(control_type)
        cmds.move(0, 0, 0, f"{control}.scalePivot", f"{control}.rotatePivot", absolute=True)
        control = cmds.rename(control, 'ctrl_' + control_name)


    # Create offset group
    offset_group = cmds.group(em=1, name='offset_' + control_name)
    cmds.parent(control, offset_group)

    # Match transform if an object is selected
    if selection_empty is False:
        cmds.matchTransform(offset_group, user_sel)
    else:
        pass


    # Set colour and thickness
    colour_value = cmds.colorIndexSliderGrp(colour_slider, query=True, value=True) - 1
    thickness_value = cmds.floatSlider(thickness_slider, query=True, value=True)

    control_shape = cmds.listRelatives(control, shapes=True)
    control_shape = control_shape[0]

    cmds.setAttr(control_shape + '.overrideEnabled', 1)
    cmds.setAttr(control_shape + '.overrideColor', colour_value)
    cmds.setAttr(control_shape + '.lineWidth', thickness_value)

    # Remove the Renderman attributes of the curve if the plugin is loaded
    renderman_loaded = cmds.pluginInfo('RenderMan_for_Maya.py', q=1, loaded=1)

    if renderman_loaded is True:
        rmanAttrsHide(control)

    cmds.select(clear=True)


def replaceControl(*args):

    # Check if selection is empty
    user_sel = cmds.ls(sl=True)

    if len(user_sel) != 1:
        cmds.error('Please select only one controller to replace')
    else:
        pass

    user_sel_shape = cmds.listRelatives(user_sel, shapes=1)
    shape_name = f'{user_sel[0]}Shape'


    # Handling menu variable
    if cmds.optionMenu('style_menu', q=True, v=True) == 'Cube':
        control_type = CUBE_POINTS
    elif cmds.optionMenu('style_menu', q=True, v=True) == 'Arrow':
        control_type = ARROW_POINTS
    elif cmds.optionMenu('style_menu', q=True, v=True) == 'Pole':
        control_type = POLE_POINTS
    elif cmds.optionMenu('style_menu', q=True, v=True) == 'Square':
        control_type = SQUARE_POINTS
    elif cmds.optionMenu('style_menu', q=True, v=True) == 'Triangle':
        control_type = TRIANGLE_POINTS
    elif cmds.optionMenu('style_menu', q=True, v=True) == 'Rotate':
        control_type = ROTATE_POINTS
    elif cmds.optionMenu('style_menu', q=True, v=True) == 'Cross':
        control_type = CROSS_POINTS


    control_name = 'TEMP_DEL'


    # Create controllers
    if cmds.optionMenu('style_menu', q=True, v=True) == 'Circle':
        control = cmds.circle(name='ctrl_' + control_name, normal=[0, 1, 0])[0]
        cmds.delete(control, ch=1)
    else:
        control = pm.language.Mel.eval(control_type)
        cmds.move(0, 0, 0, f"{control}.scalePivot", f"{control}.rotatePivot", absolute=True)
        control = cmds.rename(control, 'ctrl_' + control_name)


    # Create offset group
    offset_group = cmds.group(em=1, name='offset_' + control_name)
    cmds.parent(control, offset_group)

    # Match transform
    cmds.matchTransform(offset_group, user_sel)


    # Set colour and thickness
    colour_value = cmds.colorIndexSliderGrp(colour_slider, query=True, value=True) - 1
    thickness_value = cmds.floatSlider(thickness_slider, query=True, value=True)

    control_shape = cmds.listRelatives(control, shapes=True)
    control_shape = control_shape[0]

    cmds.setAttr(control_shape + '.overrideEnabled', 1)
    cmds.setAttr(control_shape + '.overrideColor', colour_value)
    cmds.setAttr(control_shape + '.lineWidth', thickness_value)


    # Create the replacing behaviour
    cmds.delete(user_sel_shape)
    cmds.parent(control_shape, user_sel, r=1, s=1)
    cmds.delete(offset_group)
    cmds.rename(control_shape, shape_name)

    cmds.select(cl=1)


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


#-------------------------------------------------------------------------------------------------------
# Create UI

def controllerCreatorUI():

    # Define global variables
    global text_field
    global type_menu
    global colour_slider
    global thickness_slider
    global scale_slider

    # Check if window already exists and deletes it
    if cmds.window('controllerCreatorUI', ex=True):
        cmds.deleteUI('controllerCreatorUI')

    # Create window
    window = cmds.window('controllerCreatorUI', title='Controller Creator v1.7', w=230, h=300,
                         mnb=False, mxb=False, sizeable=False)

    # Create main Layout
    main_layout = cmds.formLayout(nd=100)

    # Create Title
    title = cmds.text(label='Controller Creator', font='boldLabelFont')

    # Create Separators
    separator_01 = cmds.separator(h=5, style='shelf')
    separator_02 = cmds.separator(h=5, style='none')
    separator_03 = cmds.separator(h=5, style='in')
    separator_04 = cmds.separator(h=5, style='none')
    separator_05 = cmds.separator(h=5, style='none')

    # Create Controller Style Menu
    type_menu = cmds.optionMenu('style_menu', label='Controller Style', h=20,
                                ann='What shape do you want for your controller?')

    cmds.menuItem(label='Circle')
    cmds.menuItem(label='Cube')
    cmds.menuItem(label='Arrow')
    cmds.menuItem(label='Pole')
    cmds.menuItem(label='Pin')
    cmds.menuItem(label='Cross')
    cmds.menuItem(label='Square')
    cmds.menuItem(label='Rotate')
    cmds.menuItem(label='Triangle')

    # Create Object Name Writing Field
    text_field = cmds.textField(pht='Object Name', w=50)

    # Create Colour Slider
    colour_slider = cmds.colorIndexSliderGrp(ann='What colour do you want your controller to be?', max = 31, min = 1,
                                             value = 1, changeCommand=colourChange, label='Controller Colour')

    # Create Thickness Slider
    thickness_slider = cmds.floatSlider(ann='How thick do you want your controller to be?', max=10, min=1, value=1,
                                        step=0.5, w=50, dragCommand=thicknessChange)

    # Create Scale Slider
    scale_slider = cmds.floatSlider(ann='What size do you want your controller to be?', max=5, min=0.1, value=1,
                                    step=0.2, w=50, dragCommand=scaleChange, changeCommand=deleteHistory)

    # Create Buttons
    button = cmds.button(label='CREATE', command=createControl, ann='Create the controller')
    replace_button = cmds.button(label='REPLACE', command=replaceControl, ann='Replace the current controller shape by a new one')

    # Create Missing Titles
    object_name_title = cmds.text(label='Object Name')
    thickness_slider_title = cmds.text(label='Controller Thickness')
    scale_slider_title = cmds.text(label='Controller Scale')

    # Adjust Layout
    cmds.formLayout(main_layout, e=True,
                    attachForm = [(title, 'top', 10), (title, 'left', 5), (title, 'right', 5),

                                  (separator_01, 'left', 5), (separator_01, 'right', 5),

                                  (separator_02, 'left', 5), (separator_02, 'right', 5),

                                  (separator_03, 'left', 5), (separator_03, 'right', 5),

                                  (separator_04, 'left', 5), (separator_04, 'right', 5),

                                  (separator_05, 'left', 5), (separator_05, 'right', 5),

                                  (type_menu, 'left', 60), (type_menu, 'right', 60),

                                  (text_field, 'left', 145), (text_field, 'right', 59),

                                  (object_name_title, 'left', 60),

                                  (colour_slider, 'left', -30), (colour_slider, 'right', 20),

                                  (thickness_slider, 'left', 130), (thickness_slider, 'right', 25),

                                  (scale_slider, 'left', 130), (scale_slider, 'right', 25),

                                  (button, 'left', 5), (button, 'bottom', 5),

                                  (replace_button, 'right', 5), (replace_button, 'bottom', 5)
                    ],

                    attachControl = [(separator_01, 'top', 10, title),

                                     (type_menu, 'top', 20, separator_01),

                                     (separator_02, 'top', 5, type_menu),

                                     (text_field, 'top', 5, separator_02),

                                     (object_name_title, 'top', 5, separator_02),

                                     (separator_03, 'top', 25, object_name_title),

                                     (colour_slider, 'top', 15, separator_03),

                                     (separator_04, 'top', 5, colour_slider),

                                     (thickness_slider, 'top', 5, separator_04),

                                     (thickness_slider_title, 'top', 5, separator_04),

                                     (separator_05, 'top', 5, thickness_slider),

                                     (scale_slider, 'top', 5, separator_05),

                                     (scale_slider_title, 'top', 5, separator_05),

                                     (button, 'top', 20, scale_slider),

                                     (replace_button, 'top', 20, scale_slider),

                                     (replace_button, 'left', 5, button)
                    ],

                    attachPosition = [(thickness_slider_title, 'left', 20, 0),
                                      (scale_slider_title, 'left', 20, 0),
                                      (button, 'right', 10, 52)
                    ])

    # Show the window
    cmds.showWindow(window)


controllerCreatorUI()
