import bpy
from bpy.types import Operator, Node as OriNode, PropertyGroup
from bpy.utils import register_class, unregister_class

class Node(OriNode):
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'nPicker'

    def save(self):
        '''generate base save dict'''
        save_dict = {
            "type": self.bl_idname,
            "label": self.label,
            "location": list(self.location),
            "width": self.width,
            "height": self.height,
            "hide": self.hide,
            "parent": self.parent.name if self.parent else None,
            "use_custom_color": self.use_custom_color,
            "color": list(self.color),
        }
        return save_dict

    def load(self, save_dict, nodes):
        '''load property from save dict'''

        self.label = save_dict['label']
        self.location = tuple(save_dict['location'])
        self.width = save_dict['width']
        self.height = save_dict['height']
        self.hide = save_dict['hide']
        self.parent = nodes[save_dict['parent']]['node'] if save_dict['parent'] else None
        self.use_custom_color = save_dict['use_custom_color']
        self.color = tuple(save_dict['color'])

class NPICK_OP_BASE(Operator):
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        return context.space_data.type == "NODE_EDITOR" and context.space_data.tree_type == "nPicker" and context.space_data.node_tree is not None 

class PG_picker_row(PropertyGroup):
    name: bpy.props.StringProperty(
        name='name',
        default='row'
    )

    object_armature: bpy.props.PointerProperty(
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == "ARMATURE"
    )

    def update_picker(self, context):
        if self.picker:
            # change to false
            self.picker = False

            if self.object_armature and self.bone_name:
                # get bone
                pose_bone = self.object_armature.pose.bones.get(self.bone_name)

                if pose_bone:
                    if self.mode_select == "SINGLE":
                        # deselect bone if mode select bone is single
                        for bone in [pose_bone_to_deselect.bone for pose_bone_to_deselect in self.object_armature.pose.bones if pose_bone_to_deselect is not pose_bone]:
                            bone.select = False

                    # select bone if exist
                    pose_bone.bone.select = True

    picker: bpy.props.BoolProperty(
        default=False,
        update=update_picker
    )

    mode_select: bpy.props.EnumProperty(
        items=[
            ('MULTI', 'Muliple', 'multiple select bone'),
            ('SINGLE', 'Single', 'single select bone')
        ],
        default='SINGLE'
    )

    bone_name: bpy.props.StringProperty(
        name='bone name',
        default=''
    )

    show_bone_name: bpy.props.BoolProperty(
        name='show bone name',
        default=False
    )

class PG_picker_column(PropertyGroup):
    name: bpy.props.StringProperty(
        name='name',
        default='column'
    )

    size: bpy.props.FloatProperty(
        default=1.0
    )

    rows: bpy.props.CollectionProperty(
        type=PG_picker_row
    )

class NODE(Node):
    '''node picker'''
    bl_idname = 'NodeNPickBonePicker'
    bl_label = 'Picker'
    bl_icon = 'EYEDROPPER'
    bl_width_default = 250
    bl_width_min = 50

    mode_compact: bpy.props.BoolProperty(
        default=False
    )

    picker_columns: bpy.props.CollectionProperty(
        type=PG_picker_column
    )

    def update_mode_select(self, context):
        for picker_column in self.picker_columns:
            for picker_row in picker_column.rows:
                picker_row.mode_select = self.mode_select

    mode_select: bpy.props.EnumProperty(
        items=[
            ('MULTI', 'Muliple', 'multiple select bone'),
            ('SINGLE', 'Single', 'single select bone')
        ],
        default='SINGLE',
        update=update_mode_select
    )

    def update_object_armature(self, context):
        selected_nodes = [node for node in context.space_data.node_tree.nodes if node.select and node is not self]

        for node in selected_nodes:
            node.select = False
            if hasattr(node, 'update_object_armature'):
                node.update_object_armature(context)

        for node in selected_nodes:
            node.select = True

        if hasattr(self, 'picker_columns'):
            for picker_column in self.picker_columns:
                for picker_row in picker_column.rows:
                    picker_row.object_armature = self.object_armature

    object_armature: bpy.props.PointerProperty(
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == "ARMATURE",
        update=update_object_armature
    )

    def draw_buttons(self, context, layout):
        if not self.mode_compact:
            row = layout.row()
            split = row.split(factor=0.4)
            col = split.column()
            col.alignment = 'RIGHT'
            col.label(text='Object')
            col.label(text='Select Mode')
            col.label(text='Custom Color')
            col.label(text='Color')
            col = split.column()
            col.prop(self, 'object_armature', text='')
            col.prop(self, 'mode_select', text='')
            col.prop(self, 'use_custom_color', text='')
            col.prop(self, 'color', text='')

            row = layout.row()
            row.scale_y = 1.25
            row.prop(self, 'mode_compact', text='Compact Mode', toggle=True)

        col = layout.column()
        for index, picker_column in enumerate(self.picker_columns):

            if picker_column.rows:

                row = col.row()
                row.scale_y = picker_column.size

                for picker_row in picker_column.rows:
                    row.prop(picker_row, 'picker', text=picker_row.bone_name if bool(picker_row.bone_name) and picker_row.show_bone_name else ' ', expand=True, toggle=True, emboss=bool(picker_row.bone_name))

    def draw_buttons_ext(self, context, layout):
        row = layout.row()
        split = row.split(factor=0.4)
        col = split.column()
        col.alignment = 'RIGHT'
        col.label(text='Object')
        col.label(text='Select Mode')
        col.label(text='Custom Color')
        col.label(text='Color')
        col = split.column()
        col.prop(self, 'object_armature', text='')
        col.prop(self, 'mode_select', text='')
        col.prop(self, 'use_custom_color', text='')
        col.prop(self, 'color', text='')

        row = layout.row()
        row.scale_y = 1.25
        row.prop(self, 'mode_compact', text='Compact Mode', toggle=True)

        row = layout.row()
        op = row.operator('npick.add_column_picker')
        op.node_tree_name = self.id_data.name
        op.node_object_name = self.name
        op.is_append = False

        col = layout.column()
        for index, picker_column in enumerate(self.picker_columns):

            row = col.row(align=True)
            row.prop(picker_column, 'size')
            op = row.operator('npick.remove_column_picker', text='column', icon='REMOVE')
            op.node_tree_name = self.id_data.name
            op.node_object_name = self.name
            op.index = index
            op = row.operator('npick.add_row_picker', text='row', icon='ADD')
            op.node_tree_name = self.id_data.name
            op.node_object_name = self.name
            op.index = index

            if picker_column.rows:

                row = col.row()
                row.scale_y = picker_column.size

                for index_row, picker_row in enumerate(picker_column.rows):
                    # row.prop(picker_row, 'picker', text=' ', icon=('LAYER_USED' if picker_row.bone_name else 'BLANK1'), expand=True, toggle=True)
                    op = row.operator('npick.popup_row_picker', text=picker_row.bone_name if bool(picker_row.bone_name) else ' ')
                    op.node_tree_name = self.id_data.name
                    op.node_object_name = self.name
                    op.index_column = index
                    op.index_row = index_row

        if self.picker_columns:
            row = layout.row()
            op = row.operator('npick.add_column_picker')
            op.node_tree_name = self.id_data.name
            op.node_object_name = self.name
            op.is_append = True

    def draw_label(self):
        return "Picker"

    def save(self):
        '''generate save dict'''

        # get basic dict
        save_dict = super().save()

        save_dict['mode_compact'] =  self.mode_compact
        save_dict['mode_select'] =  self.mode_select
        save_dict['picker_columns'] =  [{'size': col.size, 'rows': [{'bone_name': row.bone_name, 'show_bone_name': row.show_bone_name} for row in col.rows]} for col in self.picker_columns]

        return save_dict

    def load(self, save_dict, nodes):
        '''load property from save dict'''

        # set basic dict
        super().load(save_dict, nodes)

        self.mode_compact = save_dict['mode_compact']
        self.mode_select = save_dict['mode_select']

        # clear collection
        self.picker_columns.clear()

        for col_data in save_dict['picker_columns']:
            new_col = self.picker_columns.add()
            new_col.size = col_data['size']

            for row_data in col_data['rows']:
                new_row = new_col.rows.add()
                new_row.bone_name = row_data['bone_name']
                new_row.show_bone_name = row_data['show_bone_name']

class NPICK_OP_add_column_picker(NPICK_OP_BASE):
    """add column on picker node"""
    bl_idname = "npick.add_column_picker"
    bl_label = "add column"

    node_tree_name: bpy.props.StringProperty(default="")
    node_object_name: bpy.props.StringProperty(default="")
    is_append: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        # get node
        node = bpy.data.node_groups[self.node_tree_name].nodes[self.node_object_name]

        # add column
        new_col = node.picker_columns.add()

        # add one row
        new_row = new_col.rows.add()

        # set current select mode
        new_row.mode_select = node.mode_select

        # set current object armature
        new_row.object_armature = node.object_armature

        if not self.is_append:
            node.picker_columns.move((len(node.picker_columns) - 1), 0)

        return {'FINISHED'}

class NPICK_OP_remove_column_picker(NPICK_OP_BASE):
    """add column on picker node"""
    bl_idname = "npick.remove_column_picker"
    bl_label = "remove column"

    node_tree_name: bpy.props.StringProperty(default="")
    node_object_name: bpy.props.StringProperty(default="")
    index: bpy.props.IntProperty(default=-1)

    def execute(self, context):
        # get node
        node = bpy.data.node_groups[self.node_tree_name].nodes[self.node_object_name]

        # remove column
        node.picker_columns.remove(self.index)

        return {'FINISHED'}

class NPICK_OP_add_row_picker(NPICK_OP_BASE):
    """add row on picker node"""
    bl_idname = "npick.add_row_picker"
    bl_label = "add row"

    node_tree_name: bpy.props.StringProperty(default="")
    node_object_name: bpy.props.StringProperty(default="")
    index: bpy.props.IntProperty(default=-1)

    def execute(self, context):
        # get node
        node = bpy.data.node_groups[self.node_tree_name].nodes[self.node_object_name]

        # add row to column
        picker_column = node.picker_columns[self.index]
        picker_row = picker_column.rows.add()

        # set current select mode
        picker_row.mode_select = node.mode_select

        # set current object armature
        picker_row.object_armature = node.object_armature

        return {'FINISHED'}

class NPICK_OP_remove_row_picker(NPICK_OP_BASE):
    """remove row on picker node"""
    bl_idname = "npick.remove_row_picker"
    bl_label = "remove row"

    node_tree_name: bpy.props.StringProperty(default="")
    node_object_name: bpy.props.StringProperty(default="")
    index_column: bpy.props.IntProperty(default=-1)
    index_row: bpy.props.IntProperty(default=-1)

    def execute(self, context):
        # get node
        node = bpy.data.node_groups[self.node_tree_name].nodes[self.node_object_name]

        # rwmove row from column
        picker_column = node.picker_columns[self.index_column]
        picker_column.rows.remove(self.index_row)

        return {'FINISHED'}

class NPICK_OP_popup_row_picker(NPICK_OP_BASE):
    """popup row on picker node"""
    bl_idname = "npick.popup_row_picker"
    bl_label = "edit row picker"
    bl_options = {"REGISTER", "UNDO"}

    node_tree_name: bpy.props.StringProperty(
        default="",
        options={'HIDDEN'}
    )

    node_object_name: bpy.props.StringProperty(
        default="",
        options={'HIDDEN'}
    )

    index_column: bpy.props.IntProperty(
        default=-1,
        options={'HIDDEN'}
    )

    index_row: bpy.props.IntProperty(
        default=-1,
        options={'HIDDEN'}
    )

    bone_name: bpy.props.StringProperty(
        name='bone',
        default='bone',
    )

    show_bone_name: bpy.props.BoolProperty(
        name='show bone name',
        default=False
    )

    def invoke(self, context, event):
        active_pose_bone = context.active_pose_bone
        self.bone_name = active_pose_bone.name if active_pose_bone else "bone"
        return context.window_manager.invoke_props_dialog(self, width = 250)

    def draw(self, context):
        layout = self.layout

        col = layout.column()

        col.prop(self, 'bone_name')
        col.prop(self, 'show_bone_name')

        row = layout.row()
        op = row.operator('npick.remove_row_picker')
        op.node_tree_name = self.node_tree_name
        op.node_object_name = self.node_object_name
        op.index_column = self.index_column
        op.index_row = self.index_row

    def execute(self, context):
        # get node
        node = bpy.data.node_groups[self.node_tree_name].nodes[self.node_object_name]

        # get row picker
        picker_row = node.picker_columns[self.index_column].rows[self.index_row]

        picker_row.bone_name = self.bone_name
        picker_row.show_bone_name = self.show_bone_name

        return {'FINISHED'}

classes = [
    PG_picker_row,
    PG_picker_column,
    NPICK_OP_add_column_picker,
    NPICK_OP_remove_column_picker,
    NPICK_OP_add_row_picker,
    NPICK_OP_remove_row_picker,
    NPICK_OP_popup_row_picker,
    NODE
]

def register():
    for x in classes:
        register_class(x)

def unregister():
    for x in reversed(classes):
        unregister_class(x)