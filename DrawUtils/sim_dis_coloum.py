import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# plt.figure(figsize=(13, 4))
# 构造x轴刻度标签、数据
labels = ['karate', 'dolphins', 'football', 'polbooks']
data = [[73, 88, 93, 58],
        [83, 88, 89, 58],
        [83, 88, 89, 58],
        [100, 88, 93, 59]]
# mod
# data = [[31, 37, 59, 49],
#         [36, 37, 57, 49],
#         [36, 37, 55, 49],
#         [37, 38, 60, 49]]
# # #
# # f-score
# data = [[94, 98, 90, 82],
#         [96, 98, 88, 75],
#         [96, 98, 87, 76],
#         [100, 98, 92, 95]]

# 'red', 'orange', 'blue', 'green'
# 四组数据
x = np.arange(len(labels))  # x轴刻度标签位置
width = 0.2  # 柱子的宽度
# 计算每个柱子在x轴上的位置，保证x轴刻度标签居中
plt.bar(x - 1.5 * width, data[0], width, color='#F38181', label='Geodesic', edgecolor='white', linewidth=2, hatch='//')
plt.bar(x - 0.5 * width, data[1], width, color='#FCE38A', label='Jaccard', edgecolor='white', hatch='\\\\')
plt.bar(x + 0.5 * width, data[2], width, color='#cff09e', label='Cosine', edgecolor='white', hatch='||||')
plt.bar(x + 1.5 * width, data[3], width, color='#95E1D3', edgecolor='white', label='SSM', hatch='----')
# plt.bar(x - 1.5 * width, data[0], width, color='#96ceb4', label='Geodesic', edgecolor='white', linewidth=2, hatch='//')
# plt.bar(x - 0.5 * width, data[1], width, color='#ffeead', label='Jaccard', edgecolor='white', hatch='\\\\')
# plt.bar(x + 0.5 * width, data[2], width, color='#ffad60', label='Cosine', edgecolor='white', hatch='||||')
# plt.bar(x + 1.5 * width, data[3], width, color='#d9534f', edgecolor='white', label='SSM', hatch='----')
plt.ylabel('NMI')
# x轴刻度标签位置不进行计算
plt.xticks(x, labels=labels)
# plt.legend()
plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=4, frameon=False, fontsize=12)

# plt.show()
plt.savefig('sim_node_nmix_00.png',dpi=750, bbox_inches="tight")

plt.show()
