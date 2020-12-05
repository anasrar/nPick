import os
import bpy
from bpy.types import Operator
from bpy.utils import register_class, unregister_class

class NPICK_OP_BASE(Operator):
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        return context.space_data.type == "NODE_EDITOR" and context.space_data.tree_type == "nPicker" and context.space_data.node_tree is not None 

class NPICK_OP_add_slot_image(NPICK_OP_BASE):
    """add slot image"""
    bl_idname = "npick.add_slot_image"
    bl_label = "add slot image"

    def execute(self, context):
        node_tree = context.space_data.node_tree

        # add new slot
        new_slot = node_tree.picker_background_images.add()

        # create texture
        new_texture = bpy.data.textures.new('bg-npick', 'IMAGE')

        # assign texture to slot
        new_slot.texture = new_texture

        return {'FINISHED'}

class NPICK_OP_remove_slot_image(NPICK_OP_BASE):
    """remove slot image"""
    bl_idname = "npick.remove_slot_image"
    bl_label = "remove"

    index: bpy.props.IntProperty(default=-1)

    def execute(self, context):
        node_tree = context.space_data.node_tree

        # get slot image
        slot = node_tree.picker_background_images[self.index]

        # remove texture
        bpy.data.textures.remove(slot.texture)

        # remove slot
        node_tree.picker_background_images.remove(self.index)

        return {'FINISHED'}

class NPICK_OP_add_image_from_view_3d(NPICK_OP_BASE):
    """add background image"""
    bl_idname = "npick.add_image_from_view_3d"
    bl_label = "add image from view 3d"

    @classmethod
    def poll(cls, context):
        # check if view exist in current screen
        is_view_3d_in_screen = next(iter([p.spaces[0] for p in context.screen.areas if p.type == "VIEW_3D"]), None)

        return context.space_data.type == "NODE_EDITOR" and context.space_data.tree_type == "nPicker" and context.space_data.node_tree is not None and is_view_3d_in_screen

    def execute(self, context):
        # render view 3d
        bpy.ops.render.opengl()

        # file path to save image
        filepath = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'tmp', 'background.png'))

        # save image
        bpy.data.images["Render Result"].save_render(filepath)

        # load image
        image = bpy.data.images.load(filepath)

        # pack image to blend file
        image.pack()

        # essentials property
        image.use_fake_user = True
        image.filepath = ''

        return {'FINISHED'}

classes = [
    NPICK_OP_add_slot_image,
    NPICK_OP_remove_slot_image,
    NPICK_OP_add_image_from_view_3d
]

# def register():
#     for x in classes:
#         register_class(x)

# def unregister():
#     for x in reversed(classes):
#         unregister_class(x)