'''
Copyright (C) 2018 Emanuel Demetrescu
emanuel.demetrescu@gmail.com

Created by EMANUEL DEMETRESCU

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "EM tools",
    "description": "Blender tools for Extended Matrix",
    "author": "E. Demetrescu",
    "version": (1, 0, 7),
    "blender": (2, 79, 0),
    "location": "Tool Shelf panel",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Tools" }


import bpy


# load and reload submodules
##################################

import importlib

import bpy.props as prop
from bpy.props import (BoolProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty,
                       IntProperty
                       )
from .functions import *
from bpy.props import StringProperty, BoolProperty, IntProperty, CollectionProperty, BoolVectorProperty, PointerProperty, FloatVectorProperty                       

from bpy.types import Menu, Panel, UIList, PropertyGroup
from . import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())

#######################################################################################################################
# per epoch manager
###################

class EM_Group(PropertyGroup):
    use_toggle = BoolProperty(name="", default=True)
    #is_wire = BoolProperty(name="", default=False)
    is_locked = BoolProperty(name="", default=False)
    is_selected = BoolProperty(name="", default=False)
                               # this is just a temporary value as a user can
                               # select/deselect
    unique_id = StringProperty(default="")

    wire_color = FloatVectorProperty(
        name="wire",
        subtype='COLOR',
        default=(0.2, 0.2, 0.2),
        min=0.0, max=1.0,
        description="wire color of the group"
    )


class EM_Object_Id(PropertyGroup):
    unique_id_object = StringProperty(default="")


class EM_Other_Settings(PropertyGroup):
    select_all_layers = BoolProperty(name="Select Visible Layers", default=True)
    unlock_obj = BoolProperty(name="Unlock Objects", default=False)
    unhide_obj = BoolProperty(name="Unhide Objects", default=True)
    em_proxy_sync = BoolProperty(name="Sync EM Proxy selection", default=True, update = settingsSwitch)
    em_proxy_sync2 = BoolProperty(name="Sync EM Proxy selection2", default=True, update = settingsSwitch)
    em_proxy_sync2_zoom = BoolProperty(name="Sync EM Proxy selection2 zoom", default=True, update = settingsSwitch)
   
#######################################################################################################################

class EMListItem(bpy.types.PropertyGroup):
    """ Group of properties representing an item in the list """

    name = prop.StringProperty(
           name="Name",
           description="A name for this item",
           default="Untitled")
    
    description = prop.StringProperty(
           name="Description",
           description="A description for this item",
           default="Empty")

    icon = prop.StringProperty(
           name="code for icon",
           description="",
           default="QUESTION")
    
    url = prop.StringProperty(
           name="url",
           description="An url behind this item",
           default="Empty")
    
    shape = prop.StringProperty(
           name="shape",
           description="The shape of this item",
           default="Empty")
    
    y_pos = prop.FloatProperty(
           name="y_pos",
           description="The y_pos of this item",
           default=0.0)
           
    epoch = prop.StringProperty(
           name="code for epoch",
           description="",
           default="Empty")           
    

class EPOCHListItem(bpy.types.PropertyGroup):
    """ Group of properties representing an item in the list """

    name = prop.StringProperty(
           name="Name",
           description="A name for this item",
           default="Untitled")
    
    id = prop.StringProperty(
           name="id",
           description="A description for this item",
           default="Empty")

    min_y = prop.FloatProperty(
           name="code for icon",
           description="",
           default=0.0)

    max_y = prop.FloatProperty(
           name="code for icon",
           description="",
           default=0.0)
           
    height = prop.FloatProperty(
           name="height of epoch row",
           description="",
           default=0.0)

class EM_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        icons_style = 'OUTLINER'
        scene = context.scene
#        layout.column_flow(align = True)
#        if self.layout_type in {'DEFAULT', 'COMPACT'}:
        layout.label(item.name, icon = item.icon)
#        icon = 'VIEWZOOM' #if epoch_manager.use_toggle else 'VIEWZOOM'
#        op = layout.operator(
#            "uslist_icon.update", text="", emboss=False, icon=icon)
#        op.group_idx = index
#        op.is_menu = False
#        op.is_select = True
        layout.label(item.description, icon='NONE', icon_value=0)
#        layout.column_flow(align = True)



# register
##################################

import traceback

def menu_func(self, context):
    self.layout.separator()


def register():
    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()

    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))

    bpy.types.Scene.em_list = prop.CollectionProperty(type = EMListItem)
    bpy.types.Scene.em_list_index = prop.IntProperty(name = "Index for my_list", default = 0)
    bpy.types.Scene.epoch_list = prop.CollectionProperty(type = EPOCHListItem)
    bpy.types.Scene.epoch_list_index = prop.IntProperty(name = "Index for epoch_list", default = 0)
    bpy.types.Scene.EM_file = StringProperty(
      name = "EM GraphML file",
      default = "",
      description = "Define the path to the EM GraphML file",
      subtype = 'FILE_PATH'
      )

######################################################################################################
#per epoch manager
##################

    bpy.types.Scene.epoch_managers = CollectionProperty(type=EM_Group)
    bpy.types.Object.em_belong_id = CollectionProperty(type=EM_Object_Id)
    bpy.types.Scene.sg_settings = PointerProperty(type=EM_Other_Settings)

    bpy.types.Scene.epoch_managers_index = IntProperty(default=-1)

    bpy.types.VIEW3D_MT_object_specials.append(menu_func)

######################################################################################################


def unregister():
    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()

######################################################################################################
#per epoch manager
##################
    del bpy.types.Scene.epoch_managers
    del bpy.types.Object.em_belong_id
    del bpy.types.Scene.sg_settings

    del bpy.types.Scene.epoch_managers_index
######################################################################################################

    print("Unregistered {}".format(bl_info["name"]))
