import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# plt.figure(figsize=(13, 4))
# 构造x轴刻度标签、数据
labels = ['adjnoun', 'karate', 'dolphins', 'football', 'polbooks']

data = [[1, 73, 88, 93, 58],
        [2, 64, 88, 93, 58],
        [24, 100, 88, 93, 59],
        [21, 100, 88, 93, 59]]

# mod
# data = [[9, 31, 37, 59, 49],
#         [9, 31, 37, 59, 49],
#         [10, 37, 37, 60, 49],
#         [10, 37, 37, 60, 49]]

# f-score
# data = [[38, 94, 98, 90, 80],
#         [38, 91, 98, 90, 82],
#         [53, 100, 98, 92, 85],
#         [50, 100, 98, 92, 85]]

# 'red', 'orange', 'blue', 'green'
# 四组数据
x = np.arange(len(labels))  # x轴刻度标签位置
width = 0.2  # 柱子的宽度
# 计算每个柱子在x轴上的位置，保证x轴刻度标签居中
plt.bar(x - 1.5 * width, data[0], width, color='bisque', label='BDR-B')
plt.bar(x - 0.5 * width, data[1], width, color='silver', label='BDR-Z')
plt.bar(x + 0.5 * width, data[2], width, color='red', edgecolor='black', label='CBDR-B')
plt.bar(x + 1.5 * width, data[3], width, color='green', edgecolor='black', label='CBDR-Z')
plt.ylabel('NMI')
# x轴刻度标签位置不进行计算
plt.xticks(x, labels=labels)
# plt.legend()
plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=4, frameon=False, fontsize=12)

plt.show()
# plt.savefig('sim_bdr_node_nmi.pdf',bbox_inches="tight")
