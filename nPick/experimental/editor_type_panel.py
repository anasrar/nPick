import bpy
from bpy.types import Panel, NodeTree, PropertyGroup
from bpy.utils import register_class, unregister_class

class NODE_NPICK_PT_background_image(Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Tool"
    bl_label = "Background Image"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "NODE_EDITOR" and context.space_data.tree_type == "nPicker" and context.space_data.node_tree is not None

    def draw(self, context):
        layout = self.layout

        node_tree = context.space_data.node_tree

        for index, image_collection in enumerate(node_tree.picker_background_images):
            box = layout.box()
            row = box.row()
            row.template_icon(image_collection.texture.preview.icon_id, scale=10.0)
            split = box.split(factor=0.4)
            col = split.column()
            col.alignment = 'RIGHT'
            col.label(text='Image')
            col.label(text='Location')
            col.label(text='Scale')
            col = split.column()
            col.prop(image_collection.texture, 'image', text='')
            row = col.row(align=True)
            row.prop(image_collection, 'location', text='')
            row = col.row(align=True)
            row.prop(image_collection, 'scale', text='')
            op = box.operator('npick.remove_slot_image')
            op.index = index

        row = layout.row()
        row.scale_y = 1.5
        row.operator('npick.add_slot_image')

        row = layout.row()
        row.scale_y = 1.5
        row.operator('npick.add_image_from_view_3d')

class PG_background_image(PropertyGroup):
    name: bpy.props.StringProperty(
        name='name',
        default='slot'
    )
    texture: bpy.props.PointerProperty(
        type=bpy.types.Texture
    )
    location: bpy.props.FloatVectorProperty(
        name='Location',
        size=2,
        subtype='XYZ',
        default=[0, 0]
    )
    scale: bpy.props.FloatVectorProperty(
        name='Scale',
        size=2,
        subtype='XYZ',
        default=[1, 1]
    )


classes = [
    NODE_NPICK_PT_background_image
    # PG_background_image
]

# def register():
#     for x in classes:
#         register_class(x)

#     # picker background group | not ready yet
#     NodeTree.picker_background_images = bpy.props.CollectionProperty(type=PG_background_image)


# def unregister():
#     for x in reversed(classes):
#         unregister_class(x)

#     # picker background group
#     del NodeTree.picker_background_images