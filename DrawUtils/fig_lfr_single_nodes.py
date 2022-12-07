import numpy as np
import matplotlib.pyplot as plt

x = ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9']
labels = ['SSCF', 'LRSCD', 'GBDR', 'SBDR']
colors = ['red', 'orange', 'blue', 'green', 'hotpink', 'turquoise', 'saddlebrown', 'yellowgreen', 'deepskyblue',
          'slategrey']
marks = ['o', 'v', '*', 's', 'p', 'P', 'X', 'D', '<', '>']
linestyles = ['dotted', 'dashed', 'dashdot', 'solid', (0, (1, 10)), (0, (1, 1)), (0, (1, 1)), (0, (5, 10)), (0, (5, 5)),
              (0, (5, 1)), (0, (3, 1, 1, 1)), (0, (3, 1, 1, 1, 1, 1))]
# 200
# nmi
# data = [[97, 98, 89, 63, 8, 5, 3, 2, 1],
#         [100, 75, 90, 53, 5, 5, 4, 2, 1],
#         [100, 100, 90, 66, 9, 8, 5, 8, 8],
#         [100, 100, 91, 71, 11, 10, 8, 11, 11]]
#
# # mod
# data = [[66, 47, 35, 23, 13, 12, 13, 12, 14],
#         [66, 33, 35, 19, 10, 11, 11, 9, 7],
#         [67, 48, 35, 25, 16, 13, 14, 14, 14],
#         [68, 49, 36, 26, 15, 14, 14, 15, 15]]
#
# # f-score
# data = [[99, 99, 95, 68, 34, 25, 23, 19, 19],
#         [100, 75, 95, 61, 30, 24, 24, 19, 17],
#         [100, 100, 95, 81, 35, 32, 32, 27, 26],
#         [100, 100, 97, 83, 36, 34, 35, 34, 35]]

#############################################
# 1000
# nmi
data = [[100, 98, 93, 81, 41, 14, 8, 6, 4],
        [100, 98, 96, 91, 44, 20, 9, 6, 5],
        [100, 100, 97, 92, 56, 24, 10, 8, 7],
        [100, 100, 98, 92, 57, 29, 11, 8, 8]]

# mod
data = [[80, 62, 47, 32, 18, 12, 12, 11, 11],
        [80, 62, 48, 35, 17, 12, 11, 11, 11],
        [80, 64, 48, 36, 22, 14, 12, 13, 14],
        [80, 65, 49, 37, 22, 15, 13, 14, 14]]

# f-score
# data = [[100, 93, 91, 75, 43, 17, 11, 9, 8],
#         [100, 94, 94, 90, 48, 25, 13, 10, 10],
#         [100, 100, 95, 94, 61, 31, 14, 12, 12],
#         [100, 100, 96, 95, 62, 32, 14, 13, 13]]
# 1001 small communities
# nmi
# data = [[100, 96, 93, 80, 55, 30, 18, 14, 12],
#         [100, 99, 98, 92, 60, 36, 20, 16, 15],
#         [100, 100, 98, 92, 70, 40, 24, 18, 16],
#         [100, 100, 98, 92, 70, 40, 23, 18, 17]]

# mod
data = [[80, 63, 48, 31, 18, 13, 10, 10, 11],
        [80, 63, 49, 37, 20, 13, 9, 9, 10],
        [80, 65, 50, 38, 24, 15, 14, 13, 13],
        [80, 65, 50, 38, 24, 16, 15, 13, 13]]

# f-score
# data = [[100, 97, 91, 83, 53, 28, 15,11, 10],
#         [100, 98, 94, 91, 60, 31, 14, 12, 11],
#         [100, 100, 95, 94, 70, 35, 18, 13, 12],
#         [100, 100, 95, 94, 70,39, 20, 13, 12]]

assert (len(labels) == len(data))
for i in range(len(labels)):
    # plt.plot([x for x in range(len(data[i]))], data[i], label=labels[i], marker=marks[i], color=colors[i], linestyle=linestyles[i])
    plt.plot(x, data[i], label=labels[i], marker=marks[i], color=colors[i], linestyle=linestyles[i])
plt.yticks(np.arange(0, 1 + 0.1, 0.1))
plt.xlabel('μ', fontsize=14)
plt.ylabel('Q', fontsize=14)
plt.ylim(0, 80)
y_ticks = np.arange(0, 90, 10)
plt.tick_params(direction='in')
plt.yticks(y_ticks)
# plt.legend(handles = [l1, l2,], labels = ['a', 'b'], loc = 'best')

plt.legend(labels=labels, bbox_to_anchor=(0.03, 0.05), loc='lower left')
plt.tight_layout()
# plt.show()
plt.savefig('lfr_1001_q.pdf')
