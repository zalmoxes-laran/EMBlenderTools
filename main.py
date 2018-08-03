import xml.etree.ElementTree as ET
import bpy
import os
import bpy.props as prop
from bpy.props import (BoolProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty,
                       IntProperty
                       )
from .functions import *

##### da qui inizia la definizione delle classi pannello

class EMToolsPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "EM"
    bl_label = "Extended Matrix"
     
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object
        box = layout.box()
        row = box.row(align=True)
        row.label(text="EM file")
        row = box.row(align=True)
        row.prop(context.scene, 'EM_file', toggle = True, text ="") 
        row = box.row(align=True)
        split = row.split()
        col = split.column()
        col.operator("import.em_graphml", icon="STICKY_UVS_DISABLE", text='(Re)Load EM file')
#        row = layout.row()
        col = split.column(align=True)
        col.operator("uslist_icon.update", icon="PARTICLE_DATA", text='Refresh icons')
        
        row = layout.row()
        layout.alignment = 'LEFT'
        row.label(text="List of US/USV in EM file:")
        row = layout.row()
        row.template_list("EM_UL_List", "EM nodes", scene, "em_list", scene, "em_list_index")

        split = layout.split()
        col = split.column()


#        if scene.em_list[scene.em_list_index].icon == 'FILE_TICK':
#            col.operator("select.fromlistitem", icon="HAND", text='proxy from list')


        # Second column, aligned
        col = split.column(align=True)
        if check_if_current_obj_has_brother_inlist(obj.name):
            col.operator("select.listitem", icon="HAND", text='list from proxy')

        if scene.em_list_index >= 0 and len(scene.em_list) > 0:
            item = scene.em_list[scene.em_list_index]
            box = layout.box()
            row = box.row(align=True)
            row.label(text="US/USV name, description:")
            row = box.row()
            row.prop(item, "name", text="")
#            row = layout.row()
#            row.label(text="Description:")
            row = box.row()
#            layout.alignment = 'LEFT'
            row.prop(item, "description", text="", slider=True)
        if obj.type in ['MESH']:  
            obj = context.object
            box = layout.box()
            row = box.row()            
            row.label(text="Override active object's name:")#: " + obj.name)
            row = box.row()
            row.prop(obj, "name", "Manual")
            row = box.row()
            row.operator("usname.toproxy", icon="OUTLINER_DATA_FONT", text='Using EM list')
                    
#### da qui si definiscono le funzioni e gli operatori


class EM_usname_OT_toproxy(bpy.types.Operator):
    bl_idname = "usname.toproxy"
    bl_label = "Use US name for selected proxy"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        scene = context.scene
        item = scene.em_list[scene.em_list_index]
        scene.objects.active.name = item.name
        update_icons(context)
        return {'FINISHED'}

class EM_update_icon_list(bpy.types.Operator):
    bl_idname = "uslist_icon.update"
    bl_label = "Update only the icons"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        update_icons(context)
        return {'FINISHED'}
       
class EM_select_list_item(bpy.types.Operator):
    bl_idname = "select.listitem"
    bl_label = "Select element in the list above from a 3D proxy"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        scene = context.scene
        obj = context.object
        select_list_element_from_obj_proxy(obj)
        return {'FINISHED'}

class EM_select_from_list_item(bpy.types.Operator):
    bl_idname = "select.fromlistitem"
    bl_label = "Select 3D proxy from the list above"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        scene = context.scene
        list_item = scene.em_list[scene.em_list_index]
        select_3D_obj(list_item.name)
        return {'FINISHED'}

class EM_import_GraphML(bpy.types.Operator):
    bl_idname = "import.em_graphml"
    bl_label = "Import the EM GraphML"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        scene = context.scene
        graphml_file = scene.EM_file
        tree = ET.parse(graphml_file)      
        EM_list_clear(context)       
        em_list_index_ema = 0
#        tree = ET.parse('/Users/emanueldemetrescu/Desktop/EM_test.graphml')
        allnodes = tree.findall('.//{http://graphml.graphdrawing.org/xmlns}node')
        for node_element in allnodes:
#            print(node_element.text)
            if EM_check_node_type(node_element) == 'node_simple': # The node is not a group or a swimlane
                if EM_check_node_us(node_element): # Check if the node is an US, SU, USV, USM or USR node
                    my_nodename, my_node_description, my_node_url, my_node_shape, my_node_y_pos = EM_extract_node_name(node_element)
                    scene.em_list.add()
                    scene.em_list[em_list_index_ema].name = my_nodename
                    scene.em_list[em_list_index_ema].icon = EM_check_GraphML_Blender(my_nodename)
                    scene.em_list[em_list_index_ema].y_pos = float(my_node_y_pos)
#                    print('-' + my_nodename + '-' + ' has an icon: ' + EM_check_GraphML_Blender(my_nodename))
                    scene.em_list[em_list_index_ema].description = my_node_description
                    em_list_index_ema += 1                    
                else:
                    pass
            if EM_check_node_type(node_element) == 'node_swimlane':
                print("swimlane node is: " + str(node_element.attrib))
                extract_epochs(node_element)
#                my_epoch, my_y_max_epoch, my_y_min_epoch = extract_epochs(node_element)
#                print(my_epoch)
        for em_i in range(len(scene.em_list)):
            #print(scene.em_list[em_i].name)
            for epoch_in in range(len(scene.epoch_list)):
                if scene.epoch_list[epoch_in].min_y < scene.em_list[em_i].y_pos < scene.epoch_list[epoch_in].max_y:
                    scene.em_list[em_i].epoch = scene.epoch_list[epoch_in].name
                    print(scene.epoch_list[epoch_in].name)
        return {'FINISHED'}