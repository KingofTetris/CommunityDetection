import matplotlib
import matplotlib.pyplot as plt
import numpy as np

'''
三柱状图
'''
plt.figure(figsize=(13, 4))
# 构造x轴刻度标签、数据
labels = ['G1', 'G2', 'G3', 'G4', 'G5']
first = [20, 34, 30, 35, 27]
second = [25, 32, 34, 20, 25]
third = [21, 31, 37, 21, 28]
fourth = [26, 31, 35, 27, 21]

# 两组数据
plt.subplot(131)
x = np.arange(len(labels)) # x轴刻度标签位置
width = 0.25 # 柱子的宽度
# 计算每个柱子在x轴上的位置，保证x轴刻度标签居中
# x - width/2，x + width/2即每组数据在x轴上的位置
plt.bar(x - width/2, first, width, label='1')
plt.bar(x + width/2, second, width, label='2')
plt.ylabel('Scores')
plt.title('2 datasets')
# x轴刻度标签位置不进行计算
plt.xticks(x, labels=labels)
plt.legend()
# 三组数据
plt.subplot(132)
x = np.arange(len(labels)) # x轴刻度标签位置
width = 0.25 # 柱子的宽度
# 计算每个柱子在x轴上的位置，保证x轴刻度标签居中
# x - width，x， x + width即每组数据在x轴上的位置
plt.bar(x - width, first, width, label='1')
plt.bar(x, second, width, label='2')
plt.bar(x + width, third, width, label='3')
plt.ylabel('Scores')
plt.title('3 datasets')
# x轴刻度标签位置不进行计算
plt.xticks(x, labels=labels)
plt.legend()
# 四组数据
plt.subplot(133)
x = np.arange(len(labels)) # x轴刻度标签位置
width = 0.2 # 柱子的宽度
# 计算每个柱子在x轴上的位置，保证x轴刻度标签居中
plt.bar(x - 1.5*width, first, width, label='1')
plt.bar(x - 0.5*width, second, width, label='2')
plt.bar(x + 0.5*width, third, width, label='3')
plt.bar(x + 1.5*width, fourth, width, label='4')
plt.ylabel('Scores')
plt.title('4 datasets')
# x轴刻度标签位置不进行计算
plt.xticks(x, labels=labels)
plt.legend()

plt.show()
