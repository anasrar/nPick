import bpy
from bpy.types import NodeTree, PropertyGroup, Menu
from bpy.utils import register_class, unregister_class

class editor_type(NodeTree):
    '''nPicker'''
    bl_idname = 'nPicker'
    bl_label = "nPicker"
    bl_icon = 'EYEDROPPER'

class NODENPICK_MT_menu(Menu):
    bl_label = "nPick"

    def draw(self, context):
        layout = self.layout

        layout.operator("npick.save_nodes")
        layout.operator("npick.load_nodes")

classes = [
    editor_type,
    NODENPICK_MT_menu
]

def extend_layout_save_load_node(self, context):
    if context.space_data.type == "NODE_EDITOR" and context.space_data.tree_type == "nPicker" and context.space_data.node_tree is not None:
        self.layout.menu("NODENPICK_MT_menu")

def register():
    for x in classes:
        register_class(x)

    # append save and load node in header
    bpy.types.NODE_MT_editor_menus.append(extend_layout_save_load_node)

def unregister():
    for x in reversed(classes):
        unregister_class(x)

    # remove save and load node in header
    bpy.types.NODE_MT_editor_menus.remove(extend_layout_save_load_node)
