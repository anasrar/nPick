import nodeitems_utils
from nodeitems_utils import NodeItem, NodeCategory as OriNodeCategory

class NodeCategory(OriNodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'nPicker'

node_categories = [
    NodeCategory('NPICK_OBJECT', "Object", items=[
        NodeItem("NodeNPickObjectLayer"),
        NodeItem("NodeNPickObjectCustomProperties"),
        NodeItem("NodeNPickObjectCustomPropertiesData")
    ]),
    NodeCategory('NPICK_BONE', "Bone", items=[
        NodeItem("NodeNPickBonePicker"),
        NodeItem("NodeNPickBoneCustomPropertiesPoseBone"),
        NodeItem("NodeNPickBoneCustomPropertiesBone")
    ]),
    NodeCategory('NPICK_LAYOUT', "Layout", items=[
        NodeItem("NodeFrame")
    ])
]

def register():
    nodeitems_utils.register_node_categories('NPICK_NODES', node_categories)

def unregister():
    nodeitems_utils.unregister_node_categories('NPICK_NODES')