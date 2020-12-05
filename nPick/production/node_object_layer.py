import bpy
from bpy.types import Node as OriNode, PropertyGroup
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

class PG_bone_layer(PropertyGroup):
    name: bpy.props.StringProperty(
        name='name',
        default='layer'
    )
    has_bone: bpy.props.BoolProperty(
        default=True
    )
    dummy_boolean: bpy.props.BoolProperty(
        default=False
    )

class NODE(Node):
    '''node layer armature'''
    bl_idname = 'NodeNPickObjectLayer'
    bl_label = 'Bone Layer'
    bl_icon = 'LONGDISPLAY'
    bl_width_default = 250

    mode_compact: bpy.props.BoolProperty(
        default=False
    )

    def update_object_armature(self, context):
        selected_nodes = [node for node in context.space_data.node_tree.nodes if node.select and node is not self]

        for node in selected_nodes:
            node.select = False
            if hasattr(node, 'update_object_armature'):
                node.update_object_armature(context)

        for node in selected_nodes:
            node.select = True

        if hasattr(self, 'collection_bone_layers'):
            if self.object_armature is not None:
                # check bones
                for index, bone_layer in enumerate(self.collection_bone_layers):
                    bone_layer.has_bone = any([bone.layers[index] for bone in self.object_armature.data.bones])
            else:
                # reset has_bone attribute
                for bone_layer in self.collection_bone_layers:
                    bone_layer.has_bone = True

    object_armature: bpy.props.PointerProperty(
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == "ARMATURE",
        update=update_object_armature
    )

    layer_with_bone: bpy.props.BoolProperty(
        default=False
    )

    collection_bone_layers: bpy.props.CollectionProperty(
        type=PG_bone_layer
    )

    def init(self, context):
        for index in range(32):
            bone_layer = self.collection_bone_layers.add()
            bone_layer.name = 'Layer ' + str(index + 1)

    def draw_buttons(self, context, layout):
        if not self.mode_compact:
            row = layout.row()
            split = row.split(factor=0.4)
            col = split.column()
            col.alignment = 'RIGHT'
            col.label(text='Object')
            col.label(text='Filter')
            col.label(text='Custom Color')
            col.label(text='Color')
            col = split.column()
            col.prop(self, 'object_armature', text='')
            col.prop(self, 'layer_with_bone', text='Layer With Bone', toggle=True)
            col.prop(self, 'use_custom_color', text='')
            col.prop(self, 'color', text='')

            row = layout.row()
            row.scale_y = 1.25
            row.prop(self, 'mode_compact', text='Compact Mode', toggle=True)

        row = layout.row()
        col = row.column(align=True)
        col.scale_y = 1.25

        # filter layer that has bones
        filter_layers = [bone_layer for bone_layer in self.collection_bone_layers if bone_layer.has_bone]

        for index, bone_layer in enumerate((filter_layers if self.layer_with_bone else self.collection_bone_layers)):

            if self.width > 300 and index in ([8, 16, 24] if self.width > 500 else [16]):
                col = row.column(align=True)
                col.scale_y = 1.25

            if self.layer_with_bone:
                if bone_layer.has_bone:
                    sub_row = col.row(align=True)
                    if self.object_armature is not None:
                        sub_row.prop(self.object_armature.data, 'layers', text='', toggle=True, icon='HIDE_OFF' if self.object_armature.data.layers[index] else 'HIDE_ON', index=index)
                    else:
                        disableRow = sub_row.row(align=True)
                        disableRow.enabled = False
                        disableRow.prop(bone_layer, 'dummy_boolean', text='', toggle=True, icon='HIDE_ON')
                    sub_row.prop(bone_layer, 'name', text='')
            else:
                sub_row = col.row(align=True)
                if self.object_armature is not None:
                    sub_row.prop(self.object_armature.data, 'layers', text='', toggle=True, icon='HIDE_OFF' if self.object_armature.data.layers[index] else 'HIDE_ON', index=index)
                else:
                    disableRow = sub_row.row(align=True)
                    disableRow.enabled = False
                    disableRow.prop(bone_layer, 'dummy_boolean', text='', toggle=True, icon='HIDE_ON')
                sub_row.prop(bone_layer, 'name', text='')

    def draw_buttons_ext(self, context, layout):
        row = layout.row()
        split = row.split(factor=0.4)
        col = split.column()
        col.alignment = 'RIGHT'
        col.label(text='Object')
        col.label(text='Filter')
        col.label(text='Custom Color')
        col.label(text='Color')
        col = split.column()
        col.prop(self, 'object_armature', text='')
        col.prop(self, 'layer_with_bone', text='Layer With Bone', toggle=True)
        col.prop(self, 'use_custom_color', text='')
        col.prop(self, 'color', text='')

        row = layout.row()
        row.scale_y = 1.25
        row.prop(self, 'mode_compact', text='Compact Mode', toggle=True)

        row = layout.row()
        col = row.column(align=True)
        col.scale_y = 1.25

        # filter layer that has bones
        filter_layers = [bone_layer for bone_layer in self.collection_bone_layers if bone_layer.has_bone]

        for index, bone_layer in enumerate((filter_layers if self.layer_with_bone else self.collection_bone_layers)):

            if self.layer_with_bone:
                if bone_layer.has_bone:
                    sub_row = col.row(align=True)
                    if self.object_armature is not None:
                        sub_row.prop(self.object_armature.data, 'layers', text='', toggle=True, icon='HIDE_OFF' if self.object_armature.data.layers[index] else 'HIDE_ON', index=index)
                    else:
                        disableRow = sub_row.row(align=True)
                        disableRow.enabled = False
                        disableRow.prop(bone_layer, 'dummy_boolean', text='', toggle=True, icon='HIDE_ON')
                    sub_row.prop(bone_layer, 'name', text='')
            else:
                sub_row = col.row(align=True)
                if self.object_armature is not None:
                    sub_row.prop(self.object_armature.data, 'layers', text='', toggle=True, icon='HIDE_OFF' if self.object_armature.data.layers[index] else 'HIDE_ON', index=index)
                else:
                    disableRow = sub_row.row(align=True)
                    disableRow.enabled = False
                    disableRow.prop(bone_layer, 'dummy_boolean', text='', toggle=True, icon='HIDE_ON')
                sub_row.prop(bone_layer, 'name', text='')

    def draw_label(self):
        return "Bone Layer"

    def save(self):
        '''generate save dict'''

        # get basic dict
        save_dict = super().save()

        save_dict['mode_compact'] =  self.mode_compact
        save_dict['layer_with_bone'] =  self.layer_with_bone
        save_dict['collection_bone_layers'] =  [layer.name for layer in self.collection_bone_layers]

        return save_dict

    def load(self, save_dict, nodes):
        '''load property from save dict'''

        # set basic dict
        super().load(save_dict, nodes)

        self.mode_compact = save_dict['mode_compact']
        self.layer_with_bone = save_dict['layer_with_bone']

        for index, layer_name in enumerate(save_dict['collection_bone_layers']):
            self.collection_bone_layers[index].name = layer_name

classes = [
    PG_bone_layer,
    NODE
]

def register():
    for x in classes:
        register_class(x)

def unregister():
    for x in reversed(classes):
        unregister_class(x)