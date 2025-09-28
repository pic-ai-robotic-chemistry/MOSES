import networkx as nx
from pyvis.network import Network
import random

G = nx.read_graphml(r"D:\CursorProj\Chem-Ontology-Constructor\tests\unit_test\query\test\lightrag\temp_rag_storage\gpt-4_1\graph_chunk_entity_relation.graphml")

from pyvis.network import Network
import random

# Create a Pyvis network with customized font
net = Network(height="100vh", notebook=True, font_color="black")

# Set global font settings to Times New Roman
net.set_options("""
var options = {
  "nodes": {
    "font": {
      "face": "Times New Roman"
    }
  }
}
""")

# Convert NetworkX graph to Pyvis network
net.from_nx(G)

# Define colors for each level
level_colors = {
    1: "#{:02x}{:02x}{:02x}".format(random.randint(200, 255), random.randint(150, 200), random.randint(150, 200)),
    2: "#{:02x}{:02x}{:02x}".format(random.randint(150, 200), random.randint(200, 255), random.randint(150, 200)),
    3: "#{:02x}{:02x}{:02x}".format(random.randint(150, 200), random.randint(150, 200), random.randint(200, 255)),
    # Add more levels if needed
}

# first_level = ("AZOBENZENE", "E-AZOBENZENE", "ISOMERIZATION MECHANISMS")
# third_level = ("C8−N14=N13−C4 DIHEDRAL ANGLE", "PHOTOCHROMIC REACTION", "ROTATION", "NΠ* STATE", "ΠΠ* STATE", "S0")
# colors = ["#6299FF", "#FFD36A", "#FF5575"]

# 为每个节点指定颜色
# for node in net.nodes:
#     if node["label"] in first_level:
#         node["color"] = colors[0]
#     elif node["label"] in third_level:
#         node["color"] = colors[1]
#     else:
#         node["color"] = colors[2]

# Helper function to get the label of a node by its id
def get_node_label(node_id):
    for node in net.nodes:
        if node["id"] == node_id:
            return node["label"]
    return None

# # 加粗特定节点之间的边
# for edge in net.edges:
#     source_label = get_node_label(edge["from"])
#     target_label = get_node_label(edge["to"])
    
#     if source_label in first_level or target_label in first_level:
#         edge["width"] = 3  # 加粗边的宽度
#     else:
#         edge["width"] = 1  # 默认边宽
        
# Save and display the network
net.show(r"D:\CursorProj\Chem-Ontology-Constructor\tests\unit_test\query\test\lightrag\temp_rag_storage\gpt-4_1\knowledge_graph.html")