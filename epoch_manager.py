# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****


#original code from: 
#    "name": "Super Grouper",
#    "author": "Paul Geraskin, Aleksey Juravlev, BA Community",


import bpy
import random
import string

from bpy.props import *
from bpy.types import Operator
from bpy.types import Menu, Panel, UIList, PropertyGroup
from bpy.props import StringProperty, BoolProperty, IntProperty, CollectionProperty, BoolVectorProperty, PointerProperty
from bpy.app.handlers import persistent

SCENE_EM = '#EM'
UNIQUE_ID_NAME = 'em_belong_id'


class EM_BasePanel(bpy.types.Panel):
    bl_label = "Epochs Manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'EM'

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        sg_settings = scene.sg_settings

        row = layout.row(align=True)
        op = row.operator(
            "epoch_manager.change_selected_objects", text="", emboss=False, icon='BBOX')
        op.sg_objects_changer = 'BOUND_SHADE'

        op = row.operator(
            "epoch_manager.change_selected_objects", text="", emboss=False, icon='WIRE')
        op.sg_objects_changer = 'WIRE_SHADE'

        op = row.operator(
            "epoch_manager.change_selected_objects", text="", emboss=False, icon='SOLID')
        op.sg_objects_changer = 'MATERIAL_SHADE'

        op = row.operator(
            "epoch_manager.change_selected_objects", text="", emboss=False, icon='RETOPO')
        op.sg_objects_changer = 'SHOW_WIRE'

        row = layout.row(align=True)
        row.operator(
            "epoch_manager.epoch_manager_add", icon='ZOOMIN', text="")
        op = row.operator(
            "epoch_manager.epoch_manager_remove", icon='ZOOMOUT', text="")
        op.group_idx = scene.epoch_managers_index

        op = row.operator(
            "epoch_manager.epoch_manager_move", icon='TRIA_UP', text="")
        op.do_move = 'UP'

        op = row.operator(
            "epoch_manager.epoch_manager_move", icon='TRIA_DOWN', text="")
        op.do_move = 'DOWN'

        row = layout.row()
        row.template_list(
            "EM_named_epoch_managers", "", scene, "epoch_managers", scene, "epoch_managers_index")

        row = layout.row()
        op = row.operator("epoch_manager.add_to_group", text="Add")
        op.group_idx = scene.epoch_managers_index

        row.operator(
            "epoch_manager.super_remove_from_group", text="Remove")
        row.operator("epoch_manager.clean_object_ids", text="Clean")
        # layout.separator()
        layout.label(text="Selection Settings:")
        row = layout.row(align=True)
        row.prop(sg_settings, "select_all_layers", text='Layers')
        row.prop(sg_settings, "unlock_obj", text='UnLock')
        row.prop(sg_settings, "unhide_obj", text='Unhide')
        row = layout.row(align=True)


class EM_named_epoch_managers(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        epoch_manager = item
#        user_preferences = context.user_preferences
        icons_style = 'OUTLINER'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(epoch_manager, "name", text="", emboss=False)

            # select operator
            icon = 'RESTRICT_SELECT_OFF' if epoch_manager.use_toggle else 'RESTRICT_SELECT_ON'
            #if icons_style == 'OUTLINER':
            icon = 'VIEWZOOM' if epoch_manager.use_toggle else 'VIEWZOOM'
            op = layout.operator(
                "epoch_manager.toggle_select", text="", emboss=False, icon=icon)
            op.group_idx = index
            op.is_menu = False
            op.is_select = True

            # lock operator
            icon = 'LOCKED' if epoch_manager.is_locked else 'UNLOCKED'
            #if icons_style == 'OUTLINER':
            icon = 'RESTRICT_SELECT_ON' if epoch_manager.is_locked else 'RESTRICT_SELECT_OFF'
            op = layout.operator(
                "epoch_manager.change_grouped_objects", text="", emboss=False, icon=icon)
            op.sg_group_changer = 'LOCKING'
            op.group_idx = index

            # view operator
            icon = 'RESTRICT_VIEW_OFF' if epoch_manager.use_toggle else 'RESTRICT_VIEW_ON'
            op = layout.operator(
                "epoch_manager.toggle_visibility", text="", emboss=False, icon=icon)
            op.group_idx = index

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'


# master menu
#class EM_Specials_Main_Menu(bpy.types.Menu):
#    bl_idname = "epoch_manager.epoch_manager_main_menu"
#    bl_label = "SuperGrouper"
#    bl_description = "Super Grouper Menu"

#    def draw(self, context):
#        layout = self.layout

#        layout.operator(EM_epoch_manager_add.bl_idname)
#        #layout.operator(EM_epoch_manager_remove.bl_idname)
#        layout.menu(EM_Remove_SGroup_Sub_Menu.bl_idname)

#        #self.layout.operator(SG_toggle_select.bl_idname)
#        #self.layout.operator(SG_toggle_visibility.bl_idname)

#        layout.separator()
#        #layout.operator(SG_add_to_group.bl_idname)
#        layout.menu(EM_Add_Objects_Sub_Menu.bl_idname)
#        layout.operator(EM_remove_from_group.bl_idname)

#        layout.separator()
#        layout.menu(EM_Select_SGroup_Sub_Menu.bl_idname, text="Select SGroup")

#        layout.menu(EM_Deselect_SGroup_Sub_Menu.bl_idname, text="Deselect SGroup")

#        layout.separator()
#        layout.menu(EM_Toggle_Visible_SGroup_Sub_Menu.bl_idname, text="SGroup Visibility")
#        layout.menu(EM_Toggle_Shading_Sub_Menu.bl_idname, text="Shade Selected")


class EM_Add_Objects_Sub_Menu(bpy.types.Menu):
    bl_idname = "epoch_manager.add_objects_sub_menu"
    bl_label = "Add Selected Objects"
    bl_description = "Add Objects Menu"

    def draw(self, context):
        layout = self.layout

        for i, e_manager in enumerate(context.scene.epoch_managers):
            op = layout.operator(EM_add_to_group.bl_idname, text=e_manager.name)
            op.group_idx = i


class EM_Remove_SGroup_Sub_Menu(bpy.types.Menu):
    bl_idname = "epoch_manager.remove_e_manager_sub_menu"
    bl_label = "Remove Super Group"
    bl_description = "Remove Super Group Menu"

    def draw(self, context):
        layout = self.layout

        for i, e_manager in enumerate(context.scene.epoch_managers):
            op = layout.operator(EM_epoch_manager_remove.bl_idname, text=e_manager.name)
            op.group_idx = i


class EM_Select_SGroup_Sub_Menu(bpy.types.Menu):
    bl_idname = "epoch_manager.select_e_manager_sub_menu"
    bl_label = "Select SGroup"
    bl_description = "Select SGroup Menu"

    def draw(self, context):
        layout = self.layout

        for i, e_manager in enumerate(context.scene.epoch_managers):
            op = layout.operator(EM_toggle_select.bl_idname, text=e_manager.name)
            op.group_idx = i
            op.is_select = True
            op.is_menu = True


class EM_Deselect_SGroup_Sub_Menu(bpy.types.Menu):
    bl_idname = "epoch_manager.deselect_e_manager_sub_menu"
    bl_label = "Deselect SGroup"
    bl_description = "Deselect SGroup Menu"

    def draw(self, context):
        layout = self.layout

        for i, e_manager in enumerate(context.scene.epoch_managers):
            op = layout.operator(EM_toggle_select.bl_idname, text=e_manager.name)
            op.group_idx = i
            op.is_select = False
            op.is_menu = True


class EM_Toggle_Visible_SGroup_Sub_Menu(bpy.types.Menu):
    bl_idname = "epoch_manager.toggle_e_manager_sub_menu"
    bl_label = "Toggle SGroup"
    bl_description = "Toggle SGroup Menu"

    def draw(self, context):
        layout = self.layout

        for i, e_manager in enumerate(context.scene.epoch_managers):
            op = layout.operator(EM_toggle_visibility.bl_idname, text=e_manager.name)
            op.group_idx = i


class EM_Toggle_Shading_Sub_Menu(bpy.types.Menu):
    bl_idname = "epoch_manager.toggle_shading_sub_menu"
    bl_label = "Toggle Shading"
    bl_description = "Toggle Shading Menu"

    def draw(self, context):
        layout = self.layout

        op = layout.operator(EM_change_selected_objects.bl_idname, text="Bound Shade")
        op.sg_objects_changer = 'BOUND_SHADE'

        op = layout.operator(EM_change_selected_objects.bl_idname, text="Wire Shade")
        op.sg_objects_changer = 'WIRE_SHADE'

        op = layout.operator(EM_change_selected_objects.bl_idname, text="Material Shade")
        op.sg_objects_changer = 'MATERIAL_SHADE'

        op = layout.operator(EM_change_selected_objects.bl_idname, text="Show Wire")
        op.sg_objects_changer = 'SHOW_WIRE'

        layout.separator()
        op = layout.operator(EM_change_selected_objects.bl_idname, text="One Side")
        op.sg_objects_changer = 'ONESIDE_SHADE'
        op = layout.operator(EM_change_selected_objects.bl_idname, text="Double Side")
        op.sg_objects_changer = 'TWOSIDE_SHADE'


def generate_id():
    # Generate unique id
    other_ids = []
    for scene in bpy.data.scenes:
        if scene != bpy.context.scene and scene.name.endswith(SCENE_EM) is False:
            for e_manager in scene.epoch_managers:
                other_ids.append(e_manager.unique_id)

    while True:
        uni_numb = None
        uniq_id_temp = ''.join(random.choice(string.ascii_uppercase + string.digits)
                               for _ in range(10))
        if uniq_id_temp not in other_ids:
            uni_numb = uniq_id_temp
            break

    other_ids = None  # clean
    return uni_numb


class EM_epoch_manager_add(bpy.types.Operator):

    """Add and select a new layer group"""
    bl_idname = "epoch_manager.epoch_manager_add"
    bl_label = "Add Epoch group"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bool(context.scene)

    def execute(self, context):
        
        scene = context.scene

        epoch_number = len(scene.epoch_list)
        
        for epoch in range(epoch_number):
    #        print(epoch_number)

            epochname = scene.epoch_list[epoch-1].name

            check_same_ids()  # check scene ids

            epoch_managers = scene.epoch_managers

            # get all ids
            all_ids = []
            for e_manager in epoch_managers:
                if e_manager.unique_id not in all_ids:
                    all_ids.append(e_manager.unique_id)

            # remove e_managers
    #       si presuppone che abbiamo già pulito le epoche
    #        for obj in context.selected_objects:
    #            for e_manager in epoch_managers:
    #                EM_del_properties_from_obj(UNIQUE_ID_NAME, all_ids, obj, True)

            # generate new id
            uni_numb = generate_id()
            all_ids = None

            group_idx = len(epoch_managers)
            new_e_manager = epoch_managers.add()
#            new_e_manager.name = "EM.%.3d" % group_idx
            new_e_manager.name = epochname
            new_e_manager.unique_id = uni_numb
            scene.epoch_managers_index = group_idx

            # add the unique id of selected objects
    #        for obj in context.selected_objects:
    #            EM_add_property_to_obj(new_e_manager.unique_id, obj)

        return {'FINISHED'}
    
#def add_sceneobj_to_epoch(epochname):

class EM_epoch_manager_remove(bpy.types.Operator):

    """Remove selected layer group"""
    bl_idname = "epoch_manager.epoch_manager_remove"
    bl_label = "Clear all epochs"
    bl_options = {'REGISTER', 'UNDO'}

    group_idx = IntProperty()

    @classmethod
    def poll(cls, context):
        return bool(context.scene)

    def execute(self, context):
        scene_parse = context.scene
        epoch_num = len(scene_parse.epoch_managers)
        for i in range(epoch_num):
            self.group_idx = scene_parse.epoch_managers_index
            # if a scene contains goups
            if scene_parse.epoch_managers:
                check_same_ids()  # check scene ids
                get_e_manager = scene_parse.epoch_managers[self.group_idx]
                if get_e_manager is not None and self.group_idx < len(scene_parse.epoch_managers):
                    e_manager_id = get_e_manager.unique_id

                    # get all ids
                    e_managers = []
                    for e_manager in scene_parse.epoch_managers:
                        e_managers.append(e_manager.unique_id)

                    # clear context scene
                    for obj in scene_parse.objects:
                        EM_del_properties_from_obj(
                            UNIQUE_ID_NAME, [e_manager_id], obj, True)

                    # clear SGR scene
                    sgr_scene_name = scene_parse.name + SCENE_EM
                    if sgr_scene_name in bpy.data.scenes:
                        sgr_scene = bpy.data.scenes[scene_parse.name + SCENE_EM]
                        for obj in sgr_scene.objects:
                            SGR_switch_object(obj, sgr_scene, scene_parse, e_manager_id)
                            EM_del_properties_from_obj(
                                UNIQUE_ID_NAME, [e_manager_id], obj, True)

                        # remove group_scene if it's empty
                        if len(sgr_scene.objects) == 0:
                            bpy.data.scenes.remove(sgr_scene)

                    # finally remove e_manager
                    scene_parse.epoch_managers.remove(self.group_idx)
                    if len(scene_parse.epoch_managers) > 0:
                        scene_parse.epoch_managers_index = len(scene_parse.epoch_managers) - 1
                    else:
                        scene_parse.epoch_managers_index = -1
#                    self.group_idx = scene_parse.epoch_managers_index
        
        return {'FINISHED'}


class EM_epoch_manager_move(bpy.types.Operator):

    """Remove selected layer group"""
    bl_idname = "epoch_manager.epoch_manager_move"
    bl_label = "Move Super Group"
    bl_options = {'REGISTER', 'UNDO'}

    do_move = EnumProperty(
        items=(('UP', 'UP', ''),
               ('DOWN', 'DOWN', '')
               ),
        default = 'UP'
    )

    @classmethod
    def poll(cls, context):
        return bool(context.scene)

    def execute(self, context):
        scene = context.scene

        # if a scene contains goups
        if scene.epoch_managers and len(scene.epoch_managers) > 1:
            e_manager_id = scene.epoch_managers[scene.epoch_managers_index].unique_id
            if scene.epoch_managers:
                move_id = None
                if self.do_move == 'UP' and scene.epoch_managers_index > 0:
                    move_id = scene.epoch_managers_index - 1
                    scene.epoch_managers.move(scene.epoch_managers_index, move_id)
                elif self.do_move == 'DOWN' and scene.epoch_managers_index < len(scene.epoch_managers) - 1:
                    move_id = scene.epoch_managers_index + 1
                    scene.epoch_managers.move(scene.epoch_managers_index, move_id)

                if move_id is not None:
                    scene.epoch_managers_index = move_id

        return {'FINISHED'}


class EM_clean_object_ids(bpy.types.Operator):

    """Remove selected layer group"""
    bl_idname = "epoch_manager.clean_object_ids"
    bl_label = "Clean Objects IDs if the objects were imported from other blend files"
    bl_options = {'REGISTER', 'UNDO'}

    # group_idx = bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return bool(context.scene)

    def execute(self, context):
        check_same_ids()  # check scene ids

        scenes_ids = []
        for scene in bpy.data.scenes:
            if scene.epoch_managers:
                for e_manager in scene.epoch_managers:
                    if e_manager.unique_id not in scenes_ids:
                        scenes_ids.append(e_manager.unique_id)

        for obj in bpy.data.objects:
            EM_del_properties_from_obj(UNIQUE_ID_NAME, scenes_ids, obj, False)

        scenes_ids = None  # clean

        return {'FINISHED'}


def SGR_get_group_scene(context):
    group_scene_name = context.scene.name + SCENE_EM

    if group_scene_name in bpy.data.scenes:
        return bpy.data.scenes[group_scene_name]

    return None


def EM_create_group_scene(context):
    group_scene_name = context.scene.name + SCENE_EM

    if context.scene.name.endswith(SCENE_EM) is False:
        if group_scene_name in bpy.data.scenes:
            return bpy.data.scenes[group_scene_name]
        else:
            return bpy.data.scenes.new(group_scene_name)

    return None


def EM_select_objects(context, ids, do_select):
    if do_select:
        scene = context.scene
        temp_scene_layers = list(scene.layers[:])  # copy layers of the scene
        for obj in scene.objects:
            if obj.em_belong_id:
                for prop in obj.em_belong_id:
                    if prop.unique_id_object in ids:
                        for i in range(20):
                            if obj.layers[i] is True:
                                if scene.layers[i] is True or scene.sg_settings.select_all_layers:
                                    # unlock
                                    if scene.sg_settings.unlock_obj:
                                        obj.hide_select = False
                                    # unhide
                                    if scene.sg_settings.unhide_obj:
                                        obj.hide = False

                                    # select
                                    obj.select = True

                                    # break if we need to select only visible
                                    # layers
                                    if scene.sg_settings.select_all_layers is False:
                                        break
                                    else:
                                        temp_scene_layers[i] = obj.layers[i]

        # set layers switching to a scene
        if scene.sg_settings.select_all_layers:
            scene.layers = temp_scene_layers
    else:
        for obj in context.selected_objects:
            if obj.em_belong_id:
                for prop in obj.em_belong_id:
                    if prop.unique_id_object in ids:
                        obj.select = False


class EM_toggle_select(bpy.types.Operator):
    bl_idname = "epoch_manager.toggle_select"
    bl_label = "Toggle Select"
    bl_description = "Toggle Select"
    bl_options = {'REGISTER', 'UNDO'}

    group_idx = IntProperty()
    is_menu = BoolProperty(name="Is Menu?", default=True)
    is_select = BoolProperty(name="Is Select?", default=True)

    def invoke(self, context, event):
        scene = context.scene
        if self.group_idx < len(scene.epoch_managers):
            # check_same_ids()  # check scene ids

            e_manager = scene.epoch_managers[self.group_idx]

            if event.ctrl is True and self.is_menu is False:
                self.is_select = False

            if e_manager.use_toggle is True:
                if self.is_select is True:

                    # add active object if no selection
                    has_selection = False
                    if context.selected_objects:
                        has_selection = True

                    EM_select_objects(context, [e_manager.unique_id], True)
                    if scene.sg_settings.unlock_obj:
                        e_manager.is_locked = False

                    # set last active object if no selection was before
                    if has_selection is False and context.selected_objects:
                        scene.objects.active = context.selected_objects[-1]

                else:
                    EM_select_objects(context, [e_manager.unique_id], False)

        return {'FINISHED'}


class EM_toggle_visibility(bpy.types.Operator):

    """Draw a line with the mouse"""
    bl_idname = "epoch_manager.toggle_visibility"
    bl_label = "Toggle Visibility"
    bl_description = "Toggle Visibility"
    bl_options = {'REGISTER', 'UNDO'}

    group_idx = IntProperty()

    def execute(self, context):
        scene = context.scene
        if self.group_idx < len(scene.epoch_managers):
            # check_same_ids()  # check scene ids

            current_e_manager = scene.epoch_managers[self.group_idx]

            # Try to get or create new GroupScene
            group_scene = SGR_get_group_scene(context)
            if group_scene is None and current_e_manager.use_toggle is True:
                group_scene = EM_create_group_scene(context)

            # if GroupScene exists now we can switch objects
            if group_scene is not None:
                if current_e_manager.use_toggle is True:
                    for obj in scene.objects:
                        SGR_switch_object(
                            obj, scene, group_scene, current_e_manager.unique_id)
                else:
                    for obj in group_scene.objects:
                        SGR_switch_object(
                            obj, group_scene, scene, current_e_manager.unique_id)
                    if len(group_scene.objects) == 0:
                        bpy.data.scenes.remove(group_scene)

            current_e_manager.use_toggle = not current_e_manager.use_toggle  # switch visibility

            # set active object so that WMenu worked
            if current_e_manager.use_toggle is False and scene.objects.active is None:
                if scene.objects:
                    scene.objects.active = scene.objects[0]
        return {'FINISHED'}

def SGR_switch_object(obj, scene_source, scene_terget, e_manager_id):
    do_switch = False
    if obj.em_belong_id:
        for prop in obj.em_belong_id:
            if prop.unique_id_object == e_manager_id:
                do_switch = True
                break

        if do_switch is True:
            layers = obj.layers[:]  # copy layers
            obj.select = False

            # if object is not already linked
            if obj.name not in scene_terget.objects:
                obj2 = scene_terget.objects.link(obj)
                obj2.layers = layers  # paste layers

            scene_source.objects.unlink(obj)
            layers = None  # clean


def sg_is_object_in_e_managers(groups_prop_values, obj):
    is_in_group = False
    for prop in obj.em_belong_id:
        if prop.unique_id_object in groups_prop_values:
            is_in_group = True
            break

    if is_in_group:
        return True
    else:
        return False


class EM_change_grouped_objects(bpy.types.Operator):
    bl_idname = "epoch_manager.change_grouped_objects"
    bl_label = "Change Grouped"
    bl_description = "Change Grouped"
    bl_options = {'REGISTER', 'UNDO'}

    sg_group_changer = EnumProperty(
        items=(('COLOR_WIRE', 'COLOR_WIRE', ''),
               ('DEFAULT_COLOR_WIRE', 'DEFAULT_COLOR_WIRE', ''),
               ('LOCKING', 'LOCKING', '')
               ),
        default = 'DEFAULT_COLOR_WIRE'
    )

    list_objects = ['LOCKING']

    group_idx = IntProperty()

    def execute(self, context):
        scene_parse = context.scene
        if scene_parse.epoch_managers:
            # check_same_ids()  # check scene ids

            e_manager = None
            if self.sg_group_changer not in self.list_objects:
                e_manager = scene_parse.epoch_managers[
                    scene_parse.epoch_managers_index]
            else:
                if self.group_idx < len(scene_parse.epoch_managers):
                    e_manager = scene_parse.epoch_managers[self.group_idx]

            if e_manager is not None and e_manager.use_toggle is True:
                for obj in scene_parse.objects:
                    if sg_is_object_in_e_managers([e_manager.unique_id], obj):
                        if self.sg_group_changer == 'COLOR_WIRE':
                            r = e_manager.wire_color[0]
                            g = e_manager.wire_color[1]
                            b = e_manager.wire_color[2]
                            obj.color = (r, g, b, 1)
                            obj.show_wire_color = True
                        elif self.sg_group_changer == 'DEFAULT_COLOR_WIRE':
                            obj.show_wire_color = False
                        elif self.sg_group_changer == 'LOCKING':
                            if e_manager.is_locked is False:
                                obj.hide_select = True
                                obj.select = False
                            else:
                                obj.hide_select = False

                # switch locking for the group
                if self.sg_group_changer == 'LOCKING':
                    if e_manager.is_locked is False:
                        e_manager.is_locked = True
                    else:
                        e_manager.is_locked = False

        return {'FINISHED'}


class EM_change_selected_objects(bpy.types.Operator):
    bl_idname = "epoch_manager.change_selected_objects"
    bl_label = "Change Selected"
    bl_description = "Change Selected"
    bl_options = {'REGISTER', 'UNDO'}

    sg_objects_changer = EnumProperty(
        items=(('BOUND_SHADE', 'BOUND_SHADE', ''),
               ('WIRE_SHADE', 'WIRE_SHADE', ''),
               ('MATERIAL_SHADE', 'MATERIAL_SHADE', ''),
               ('SHOW_WIRE', 'SHOW_WIRE', ''),
               ('ONESIDE_SHADE', 'ONESIDE_SHADE', ''),
               ('TWOSIDE_SHADE', 'TWOSIDE_SHADE', '')
               ),
        default = 'MATERIAL_SHADE'
    )
    sg_do_with_groups = [
        'COLOR_WIRE', 'DEFAULT_COLOR_WIRE', 'LOCKED', 'UNLOCKED']

    def execute(self, context):
        for obj in context.selected_objects:
            if self.sg_objects_changer == 'BOUND_SHADE':
                obj.draw_type = 'BOUNDS'
                obj.show_wire = False
            elif self.sg_objects_changer == 'WIRE_SHADE':
                obj.draw_type = 'WIRE'
                obj.show_wire = False
            elif self.sg_objects_changer == 'MATERIAL_SHADE':
                obj.draw_type = 'TEXTURED'
                obj.show_wire = False
            elif self.sg_objects_changer == 'SHOW_WIRE':
                obj.draw_type = 'TEXTURED'
                obj.show_wire = True
            elif self.sg_objects_changer == 'ONESIDE_SHADE':
                if obj.type == 'MESH':
                    obj.data.show_double_sided = False
            elif self.sg_objects_changer == 'TWOSIDE_SHADE':
                if obj.type == 'MESH':
                    obj.data.show_double_sided = True

        return {'FINISHED'}


class EM_add_to_group(bpy.types.Operator):
    bl_idname = "epoch_manager.add_to_group"
    bl_label = "Add Selected Objects"
    bl_description = "Add To Super Group"
    bl_options = {'REGISTER', 'UNDO'}

    group_idx = IntProperty()

    def execute(self, context):
        scene_parse = context.scene

        if scene_parse.epoch_managers:
            check_same_ids()  # check ids

            # remove e_managers
            ids = []
            for e_manager in scene_parse.epoch_managers:
                ids.append(e_manager.unique_id)
            for obj in context.selected_objects:
                for e_manager in scene_parse.epoch_managers:
                    EM_del_properties_from_obj(UNIQUE_ID_NAME, ids, obj, True)
            ids = None

            e_manager = scene_parse.epoch_managers[self.group_idx]
            if e_manager is not None and self.group_idx < len(scene_parse.epoch_managers):
                for obj in context.selected_objects:
                    # add the unique id of selected group
                    EM_add_property_to_obj(e_manager.unique_id, obj)

                    # switch locking for obj
                    if e_manager.is_locked is True:
                        obj.hide_select = True
                        obj.select = False
                    else:
                        obj.hide_select = False

                    # check if the group is hidden
                    if e_manager.use_toggle is False:
                        # Try to get or create new GroupScene
                        group_scene = SGR_get_group_scene(context)
                        if group_scene is None:
                            group_scene = EM_create_group_scene(context)

                        # Unlink object
                        if group_scene is not None:
                            group_scene.objects.link(obj)
                            context.scene.objects.unlink(obj)

        return {'FINISHED'}


class EM_remove_from_group(bpy.types.Operator):
    bl_idname = "epoch_manager.super_remove_from_group"
    bl_label = "Remove Selected Objects"
    bl_description = "Remove from Super Group"
    bl_options = {'REGISTER', 'UNDO'}

    # group_idx = bpy.props.IntProperty()

    def execute(self, context):
        scene = context.scene

        if scene.epoch_managers:
            check_same_ids()  # check ids

            # get all ids
            e_managers = []
            for e_manager in scene.epoch_managers:
                e_managers.append(e_manager.unique_id)

            # remove e_managers
            for obj in context.selected_objects:
                EM_del_properties_from_obj(UNIQUE_ID_NAME, e_managers, obj, True)
            e_managers = None  # clear

        return {'FINISHED'}


def EM_add_property_to_obj(prop_name, obj):
    props = obj.em_belong_id

    has_value = False
    if props:
        for prop in props:
            if prop.unique_id_object == prop_name:
                has_value = True
                break

    # add the value if it does not exist
    if has_value == False:
        added_prop = props.add()
        added_prop.unique_id_object = prop_name


def EM_del_properties_from_obj(prop_name, e_managers_ids, obj, delete_in_e_managers=True):
    props = obj.em_belong_id

    if len(props.values()) > 0:

        # remove item
        prop_len = len(props)
        index_prop = 0
        for i in range(prop_len):
            prop_obj = props[index_prop]
            is_removed = False
            if prop_obj.unique_id_object in e_managers_ids and delete_in_e_managers == True:
                props.remove(index_prop)
                is_removed = True
            elif prop_obj.unique_id_object not in e_managers_ids and delete_in_e_managers == False:
                props.remove(index_prop)
                is_removed = True

            if is_removed is False:
                index_prop += 1

        if len(props.values()) == 0:
            del bpy.data.objects[obj.name][prop_name]


def check_same_ids():
    scenes = bpy.data.scenes
    current_scene = bpy.context.scene

    check_scenes = []
    for scene in scenes:
        if scene.name.endswith(SCENE_EM) is False and scene != current_scene:
            check_scenes.append(scene)

    if check_scenes:
        other_ids = []
        for scene in check_scenes:
            for e_manager in scene.epoch_managers:
                if e_manager.unique_id not in other_ids:
                    other_ids.append(e_manager.unique_id)

        all_obj_list = None

        if other_ids:
            for i in range(len(current_scene.epoch_managers)):
                current_e_manager = current_scene.epoch_managers[i]
                current_id = current_e_manager.unique_id
                if current_id in other_ids:
                    new_id = generate_id()

                    if all_obj_list is None:
                        all_obj_list = []
                        all_obj_list += current_scene.objects
                        group_scene = SGR_get_group_scene(bpy.context)
                        if group_scene is not None:
                            all_obj_list += group_scene.objects

                    for obj in all_obj_list:
                        has_id = False
                        for prop in obj.em_belong_id:
                            if prop.unique_id_object == current_e_manager.unique_id:
                                has_id = True
                                break
                        if has_id == True:
                            EM_add_property_to_obj(new_id, obj)

                    # set new id
                    current_e_manager.unique_id = new_id

    # clean
    check_scenes = None
    all_obj_list = None
    other_ids = None

# registration


#def register():
#    bpy.utils.register_module(__name__)

#    bpy.types.Scene.epoch_managers = CollectionProperty(type=EM_Group)
#    bpy.types.Object.em_belong_id = CollectionProperty(type=EM_Object_Id)
#    bpy.types.Scene.sg_settings = PointerProperty(type=EM_Other_Settings)

#    # Unused, but this is needed for the TemplateList to work...
#    bpy.types.Scene.epoch_managers_index = IntProperty(default=-1)

#    bpy.types.VIEW3D_MT_object_specials.append(menu_func)


#def unregister():
#    import bpy

#    del bpy.types.Scene.epoch_managers
#    del bpy.types.Object.em_belong_id
#    del bpy.types.Scene.sg_settings

#    del bpy.types.Scene.epoch_managers_index

#-----    bpy.types.VIEW3D_MT_object_specials.remove(menu_func)

#    bpy.utils.unregister_module(__name__)


#if __name__ == "__main__":
#    register()