import os
import json
import bpy
from bpy.types import Operator, Menu, NodeFrame
from bpy.utils import register_class, unregister_class
from bpy_extras.io_utils import ExportHelper, ImportHelper

class NPICK_OP_BASE(Operator):
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        return context.space_data.type == "NODE_EDITOR" and context.space_data.tree_type == "nPicker" and context.space_data.node_tree is not None 

class NPICK_OP_switch_compact_mode(NPICK_OP_BASE):
    """switch compact mode on selected node"""
    bl_idname = "npick.switch_compact_mode"
    bl_label = "switch compact mode"

    mode: bpy.props.BoolProperty(
        default=False
    )

    def execute(self, context):
        # store selected nodes
        selected_nodes = context.selected_nodes

        for node in context.selected_nodes:
            # change mode_compact in all selected node if exist
            if hasattr(node, 'mode_compact'):
                node.mode_compact = self.mode

        # update current node tree with deselect operator
        bpy.ops.node.select_all(action='DESELECT')

        # reselect node
        for node in selected_nodes:
            node.select = True
        return {'FINISHED'}

class NPICK_OP_switch_select_picker_mode(NPICK_OP_BASE):
    """switch select picker mode on selected node"""
    bl_idname = "npick.switch_select_picker_mode"
    bl_label = "switch select picker mode"

    mode: bpy.props.EnumProperty(
        items=[
            ('MULTI', 'Muliple', 'multiple select bone'),
            ('SINGLE', 'Single', 'single select bone')
        ],
        default='SINGLE'
    )

    def execute(self, context):
        # store selected nodes
        selected_nodes = context.selected_nodes

        for node in context.selected_nodes:
            # change mode_select in all selected node if exist
            if hasattr(node, 'mode_select'):
                node.mode_select = self.mode

        # update current node tree with deselect operator
        bpy.ops.node.select_all(action='DESELECT')

        # reselect node
        for node in selected_nodes:
            node.select = True
        return {'FINISHED'}

class NPICK_OP_save_nodes(NPICK_OP_BASE, ExportHelper):
    """save current nodes in node tree to json file"""
    bl_idname = "npick.save_nodes"
    bl_label = "save nodes"

    filename_ext = ".json"

    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255
    )

    def execute(self, context):
        save_dict = {
            "version": [0, 0, 1],
            "nodes": {}
        }
        for node in context.space_data.node_tree.nodes:
            # get node save dict
            if hasattr(node, 'save') and callable(node.save):
                save_dict['nodes'][node.name] = node.save()
            # save dict for frame
            elif isinstance(node, NodeFrame):
                save_dict['nodes'][node.name] = {
                    "type": node.bl_idname,
                    "label": node.label,
                    "location": list(node.location),
                    "width": node.width,
                    "height": node.height,
                    "hide": node.hide,
                    "parent": node.parent.name if node.parent else None,
                    "use_custom_color": node.use_custom_color,
                    "color": list(node.color),
                    "label_size": node.label_size,
                    "shrink": node.shrink
                }

        # save to the file
        file = open(self.filepath, "w+")
        file.write(json.dumps(save_dict, indent=4))
        file.close()

        # simple alert
        self.report({'INFO'}, "SAVE SUCCESS")

        return {'FINISHED'}

class NPICK_OP_load_nodes(NPICK_OP_BASE, ImportHelper):
    """load nodes from json file"""
    bl_idname = "npick.load_nodes"
    bl_label = "load nodes"

    filename_ext = ".json"

    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255
    )

    def execute(self, context):
        # load the file
        file = open(self.filepath, "r")
        nodes_data = json.loads(file.read())
        file.close()

        # dict nodes for parent
        parent_nodes = {}

        for node_name, node_data in nodes_data['nodes'].items():
            # new node
            new_node = context.space_data.node_tree.nodes.new(node_data['type'])

            parent_nodes[node_name] = {
                'node': new_node
            }

            # load property
            if not isinstance(new_node, NodeFrame):
                new_node.load(node_data, parent_nodes)
            else:
                new_node.label = node_data['label']
                new_node.location = tuple(node_data['location'])
                new_node.width = node_data['width']
                new_node.height = node_data['height']
                new_node.hide = node_data['hide']
                new_node.parent = nodes[node_data['parent']]['node'] if node_data['parent'] else None
                new_node.use_custom_color = node_data['use_custom_color']
                new_node.color = tuple(node_data['color'])
                new_node.label_size = node_data['label_size']
                new_node.shrink = node_data['shrink']

        # simple alert
        self.report({'INFO'}, "LOAD SUCCESS")

        return {'FINISHED'}

class NPICK_MT_PIE_menu(Menu):
    bl_label = "nPick Pie Menu"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "NODE_EDITOR" and context.space_data.tree_type == "nPicker" and context.space_data.node_tree is not None 

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()

        op = pie.operator('npick.switch_compact_mode', icon='NODE_SEL', text='Disable Compact Mode')
        op.mode = False
        op = pie.operator('npick.switch_compact_mode', icon='NODE_SEL', text='Enable Compact Mode')
        op.mode = True
        pie.row()
        pie.row()
        op = pie.operator('npick.switch_select_picker_mode', icon='NODE_SEL', text='Select Multiple Bone Mode')
        op.mode = 'MULTI'
        op = pie.operator('npick.switch_select_picker_mode', icon='NODE_SEL', text='Select Single Bone Mode')
        op.mode = 'SINGLE'

classes = [
    NPICK_OP_switch_compact_mode,
    NPICK_OP_switch_select_picker_mode,
    NPICK_OP_save_nodes,
    NPICK_OP_load_nodes,
    NPICK_MT_PIE_menu
]

addon_keymaps = []

def register():
    for x in classes:
        register_class(x)

    # register shortcut
    window_manager = bpy.context.window_manager
    keyconfig = window_manager.keyconfigs.addon
    if keyconfig:
        keymap = keyconfig.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
        # pie shortcut
        keymap_item = keymap.keymap_items.new(
            'wm.call_menu_pie',
            'E',
            'PRESS',
            ctrl=False,
            shift=True
        )
        keymap_item.properties.name = 'NPICK_MT_PIE_menu'
        addon_keymaps.append((keymap, keymap_item))
    else:
        print('Keymap Error')



def unregister():
    for x in reversed(classes):
        unregister_class(x)

    # unregister shortcut
    for keymap, keymap_item in addon_keymaps:
        keymap.keymap_items.remove(keymap_item)

    addon_keymaps.clear()
