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
    "version": (1, 0, 6),
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

from . import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())


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

class EM_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        icons_style = 'OUTLINER'
        scene = context.scene
#        layout.column_flow(align = True)
#        if self.layout_type in {'DEFAULT', 'COMPACT'}:
        layout.label(item.name, icon = item.icon)
#        icon = 'VIEWZOOM' #if super_group.use_toggle else 'VIEWZOOM'
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

def unregister():
    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()

    print("Unregistered {}".format(bl_info["name"]))
