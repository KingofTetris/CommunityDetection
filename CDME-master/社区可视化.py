import networkx as nx
import matplotlib.pyplot as plt

# 读取分区文件
with open("./output/football_partition.txt") as f:
    partition_lines = f.readlines()

# 构建节点到社区的映射
node_to_community = {}
for i, line in enumerate(partition_lines):
    community = i + 1
    nodes = [int(x) for x in line.strip().split(",") if x]
    for node in nodes:
        node_to_community[node] = community

# 构建网络
G = nx.Graph()

# 添加节点和边
with open("./dataset/football.dat") as f:
    for line in f:
        u, v = map(int, line.strip().split())
        G.add_edge(u, v)

# 定义每个社区的颜色和形状
community_colors = {1: 'blue', 2: 'red', 3: 'green', 4: 'orange', 5: 'purple', 6: 'brown', 7: 'pink', 8: 'gray', 9: 'olive', 10: 'cyan', 11: 'magenta', 12: 'yellow'}

# node_shapes = {1: 'o', 2: '^', 3: 's', 4: 'p', 5: '*', 6: 'h', 7: 'H', 8: '+', 9: 'x', 10: 'D', 11: 'd', 12: 'v'}

# 将同一个社区的节点尽量紧凑在一起形成堆
pos = nx.spring_layout(G, seed=42)

# 为不同的社区设置不同的颜色和形状，并绘制节点和边
for community in set(node_to_community.values()):
    nodes_in_community = [node for node, comm in node_to_community.items() if comm == community]
    nx.draw_networkx_nodes(G, pos, nodelist=nodes_in_community, node_color=community_colors[community], node_size=150)
nx.draw_networkx_edges(G, pos, alpha=0.5)

# 给节点添加标签 不用标签
# nx.draw_networkx_labels(G, pos, font_color='black', font_size=8)

# 设置坐标轴
plt.axis("off")

# 显示图形
plt.show()
