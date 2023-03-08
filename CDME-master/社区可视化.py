import networkx as nx
import matplotlib.pyplot as plt

# 读入分区文件
with open("./output/dolphins_partition.txt") as f:
    partitions = [list(map(int, line.strip().split(', '))) for line in f.readlines()]

# 创建无向图
G = nx.Graph()

# 添加节点
for i in range(1, 63):
    G.add_node(i)

# 添加边
with open("./dataset/dolphins.dat") as f:
    for line in f.readlines():
        edge = tuple(map(int, line.strip().split()))
        G.add_edge(*edge)

# 设置节点颜色
colors = ['r', 'b', 'g', 'c', 'm', 'y', 'k']  # 可以自定义颜色
color_map = {}
for i, partition in enumerate(partitions):
    for node in partition:
        color_map[node] = colors[i % len(colors)]

# 绘制图形
pos = nx.spring_layout(G, seed=42)  # 使用spring布局算法进行节点布局
nx.draw_networkx_nodes(G, pos, node_color=[color_map[node] for node in G.nodes()])
nx.draw_networkx_edges(G, pos)
plt.axis("off")
plt.show()