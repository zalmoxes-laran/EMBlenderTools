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
    node_y_pos = None
    nodeshape = None
    nodeurl = None
    nodedescription = None
    nodename = None
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
                nodeshape = USshape.attrib['type']
#                print(nodeshape)
            for geometry in subnode.findall('./{http://www.yworks.com/xml/graphml}ShapeNode/{http://www.yworks.com/xml/graphml}Geometry'):
                node_y_pos = geometry.attrib['y']
    if not is_d4:
        nodeurl = '--None--'
    if not is_d5:
        nodedescription = '--None--'
    return nodename, nodedescription, nodeurl, nodeshape, node_y_pos 

def EM_check_node_type(node_element):
    id_node = str(node_element.attrib)
#    print(id_node)
    if "yfiles.foldertype" in id_node:
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
    US_nodes_list = ['rectangle', 'parallelogram', 'ellipse', 'hexagon']
    my_nodename, my_node_description, my_node_url, my_node_shape, my_node_y_pos = EM_extract_node_name(node_element)
#    print(my_node_shape)
    if my_node_shape in US_nodes_list:
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

def epoch_list_clear(context):
    scene = context.scene
    scene.epoch_list.update()
    list_lenght = len(scene.epoch_list)
    for x in range(list_lenght):
        scene.epoch_list.remove(0)
    return

#Check the presence-absence of US against the GraphML
def EM_check_GraphML_Blender(node_name):
    data = bpy.data
    icon_check = 'CANCEL'
    for ob in data.objects:
        if ob.name == node_name:
            icon_check = 'FILE_TICK'
    return icon_check

def select_3D_obj(name):
    scene = bpy.context.scene
    bpy.ops.object.select_all(action="DESELECT")
    object_to_select = bpy.data.objects[name]
    object_to_select.select = True
    scene.objects.active = object_to_select
    
def update_icons(context):
    scene = context.scene
    for US in scene.em_list:
        US.icon = EM_check_GraphML_Blender(US.name)
    return

def select_list_element_from_obj_proxy(obj):
    scene = bpy.context.scene
    index_list = 0
    for i in scene.em_list:
        if obj.name == i.name:
            scene.em_list_index = index_list
        index_list += 1
        
        
def extract_epochs(node_element):
    geometry = node_element.find('.//{http://www.yworks.com/xml/graphml}Geometry')
    y_start = float(geometry.attrib['y'])
    print(y_start)
    context = bpy.context
    scene = context.scene    
#    root.findall("./country/neighbor")
    epoch_list_clear(context)  
    epoch_list_index_ema = 0   
    for nodelabel in node_element.findall('./{http://graphml.graphdrawing.org/xmlns}data/{http://www.yworks.com/xml/graphml}TableNode/{http://www.yworks.com/xml/graphml}NodeLabel'):
        RowNodeLabelModelParameter = nodelabel.find('.//{http://www.yworks.com/xml/graphml}RowNodeLabelModelParameter')
        if RowNodeLabelModelParameter is not None:
            label_node = nodelabel.text
            id_node = RowNodeLabelModelParameter.attrib['id']
            scene.epoch_list.add()
            scene.epoch_list[epoch_list_index_ema].name = str(label_node)
            scene.epoch_list[epoch_list_index_ema].id = str(id_node)
#            print("Il nodo " + str(label_node) + " ha un id: "+ str(id_node))
#            print("Il nodo " + str(scene.epoch_list[epoch_list_index_ema].name) + " ha un id: "+ str(scene.epoch_list[epoch_list_index_ema].id))

#            scene.em_list[em_list_index_ema].description = my_node_description
            epoch_list_index_ema += 1 
        else:
            pass
    y_min = y_start
    y_max = y_start
    for row in node_element.findall('./{http://graphml.graphdrawing.org/xmlns}data/{http://www.yworks.com/xml/graphml}TableNode/{http://www.yworks.com/xml/graphml}Table/{http://www.yworks.com/xml/graphml}Rows/{http://www.yworks.com/xml/graphml}Row'):
        id_row = row.attrib['id']
        h_row = float(row.attrib['height'])
        index = 0

        for i in range(len(scene.epoch_list)):
            id_key = scene.epoch_list[i].id
            if id_row == id_key:
                y_min = y_max
                y_max += h_row
                scene.epoch_list[i].min_y = y_min
                scene.epoch_list[i].max_y = y_max
#                print("il nodo "+ str(scene.epoch_list[i].name) + " con id: " + str(scene.epoch_list[i].id) + " ha y min: " + str(scene.epoch_list[i].min_y) + " e y max: " + str(scene.epoch_list[i].max_y))
