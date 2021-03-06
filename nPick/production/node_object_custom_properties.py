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

class NODE(Node):
    '''node object custom properties'''
    bl_idname = 'NodeNPickObjectCustomProperties'
    bl_label = 'Custom Properties'
    bl_icon = 'PROPERTIES'
    bl_width_default = 250

    mode_compact: bpy.props.BoolProperty(
        default=False
    )

    object_armature: bpy.props.PointerProperty(
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == "ARMATURE"
    )

    def draw_buttons(self, context, layout):
        if not self.mode_compact:
            row = layout.row()
            split = row.split(factor=0.4)
            col = split.column()
            col.alignment = 'RIGHT'
            col.label(text='Object')
            col.label(text='Custom Color')
            col.label(text='Color')
            col = split.column()
            col.prop(self, 'object_armature', text='')
            col.prop(self, 'use_custom_color', text='')
            col.prop(self, 'color', text='')

            row = layout.row()
            row.scale_y = 1.25
            row.prop(self, 'mode_compact', text='Compact Mode', toggle=True)

        if self.object_armature is not None:
            if self.object_armature.get('_RNA_UI', False):
                RNA_UI = self.object_armature['_RNA_UI']
                keys = RNA_UI.keys()
                keys.sort()
                for key in keys:
                    split = layout.split(factor=0.4)
                    col = split.column()
                    col.alignment = 'RIGHT'
                    col.label(text=key)
                    col = split.column()
                    col.prop(self.object_armature, '["' + key + '"]', text='')
            else:
                layout.label(text='Object Does Not Have Any Custom Properties')

    def draw_buttons_ext(self, context, layout):
        row = layout.row()
        split = row.split(factor=0.4)
        col = split.column()
        col.alignment = 'RIGHT'
        col.label(text='Object')
        col.label(text='Custom Color')
        col.label(text='Color')
        col = split.column()
        col.prop(self, 'object_armature', text='')
        col.prop(self, 'use_custom_color', text='')
        col.prop(self, 'color', text='')

        row = layout.row()
        row.scale_y = 1.25
        row.prop(self, 'mode_compact', text='Compact Mode', toggle=True)

        if self.object_armature is not None:
            if self.object_armature.get('_RNA_UI', False):
                RNA_UI = self.object_armature['_RNA_UI']
                keys = RNA_UI.keys()
                keys.sort()
                for key in keys:
                    split = layout.split(factor=0.4)
                    col = split.column()
                    col.alignment = 'RIGHT'
                    col.label(text=key)
                    col = split.column()
                    col.prop(self.object_armature, '["' + key + '"]', text='')
            else:
                layout.label(text='Object Does Not Have Any Custom Properties')

    def draw_label(self):
        return "Custom Properties"

    def save(self):
        '''generate save dict'''

        # get basic dict
        save_dict = super().save()

        save_dict['mode_compact'] =  self.mode_compact

        return save_dict

    def load(self, save_dict, nodes):
        '''load property from save dict'''

        # set basic dict
        super().load(save_dict, nodes)

        self.mode_compact = save_dict['mode_compact']

classes = [
    NODE
]

def register():
    for x in classes:
        register_class(x)

def unregister():
    for x in reversed(classes):
        unregister_class(x)