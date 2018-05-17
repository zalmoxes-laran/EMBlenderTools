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
        if scene.em_list[scene.em_list_index].icon == 'FILE_TICK':
            col.operator("select.fromlistitem", icon="HAND", text='proxy from list')
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


def check_if_current_obj_has_brother_inlist(obj_name):
    scene = bpy.context.scene
    for us_usv in scene.em_list:
        if us_usv.name == obj_name:
            is_brother = True
            return is_brother
    is_brother = False
    return is_brother

def EM_extract_node_name(node_element):
    is_d4 = False
    is_d5 = False
    for subnode in node_element.findall('.//{http://graphml.graphdrawing.org/xmlns}data'):
        attrib = subnode.attrib
        if attrib == {'key': 'd4'}:
            is_d4 = True
            nodeurl = subnode.text
        if attrib == {'key': 'd5'}:
            is_d5 = True
            nodedescription = subnode.text
        if attrib == {'key': 'd6'}:
            for USname in subnode.findall('.//{http://www.yworks.com/xml/graphml}NodeLabel'):
                nodename = USname.text
#                print(nodename)
            for USshape in subnode.findall('.//{http://www.yworks.com/xml/graphml}Shape'):
                nodeshape = USshape.attrib
#                print(nodeshape)        
    if not is_d4:
        nodeurl = '--None--'
    if not is_d5:
        nodedescription = '--None--'
    return nodename, nodedescription, nodeurl, nodeshape 

def EM_check_node_type(node_element):
    id_node = str(node_element.attrib)
    if id_node.startswith("{'yfiles.foldertype': 'group', 'id':"):
        tablenode = node_element.find('.//{http://www.yworks.com/xml/graphml}TableNode')
#        print(tablenode.attrib)
        if tablenode is not None:
#            print(' un nodo swimlane: ' + id_node)
            node_type = 'node_swimlane'
        else:
#            print(' un nodo group: ' + id_node)
            node_type = 'node_group'
    else:
#        print(' un semplice nodo: ' + id_node)
        node_type = 'node_simple'
    return node_type

def EM_check_node_us(node_element):
    us_name = node_element.find('.//{http://www.yworks.com/xml/graphml}NodeLabel')
    if us_name.text.startswith("SU") or us_name.text.startswith("USV") or us_name.text.startswith("USM") or us_name.text.startswith("USR"):
        id_node_us = True
    else:
        id_node_us = False
    return id_node_us

def EM_list_clear(context):
    scene = context.scene
    scene.em_list.update()
    list_lenght = len(scene.em_list)
    for x in range(list_lenght):
        scene.em_list.remove(0)
    return

#Check the presence-absence of US against the GraphML
def EM_check_GraphML_Blender(node_name):
    data = bpy.data
    icon_check = 'CANCEL'
    for ob in data.objects:
        if ob.name == node_name:
            icon_check = 'FILE_TICK'
    return icon_check

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

def select_3D_obj(name):
    scene = bpy.context.scene
    bpy.ops.object.select_all(action="DESELECT")
    object_to_select = bpy.data.objects[name]
    object_to_select.select = True
    scene.objects.active = object_to_select
       
class EM_select_list_item(bpy.types.Operator):
    bl_idname = "select.listitem"
    bl_label = "Select element in the list above from a 3D proxy"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        scene = context.scene
        obj = context.object
        index_list = 0
        for i in scene.em_list:
            if obj.name == i.name:
                scene.em_list_index = index_list
            index_list += 1
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
            print(node_element.text)
            if EM_check_node_type(node_element) == 'node_simple': # The node is not a group or a swimlane
                if EM_check_node_us(node_element): # Check if the node is an US, SU, USV, USM or USR node
                    my_nodename, my_node_description, my_node_url, my_node_shape = EM_extract_node_name(node_element)
                    scene.em_list.add()
                    scene.em_list[em_list_index_ema].name = my_nodename
                    scene.em_list[em_list_index_ema].icon = EM_check_GraphML_Blender(my_nodename)
#                    print('-' + my_nodename + '-' + ' has an icon: ' + EM_check_GraphML_Blender(my_nodename))
                    scene.em_list[em_list_index_ema].description = my_node_description
                    em_list_index_ema += 1                    
                else:
                    pass
            else:
                pass        
        return {'FINISHED'}

def update_icons(context):
    scene = context.scene
    for US in scene.em_list:
        US.icon = EM_check_GraphML_Blender(US.name)
    return
