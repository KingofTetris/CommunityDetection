'''
import numpy as np
import matplotlib.pyplot as plt

# plt.style.use(['science', 'no-latex'])
x = ['100', '200', '400', '600', '800', '1000']
labels = ['SSCF', 'LRSCD', 'GBDR', 'SBDR']
colors = ['red', 'orange', 'blue', 'green', 'hotpink', 'turquoise', 'saddlebrown', 'yellowgreen', 'deepskyblue',
          'slategrey']
marks = ['o', 'v', '*', 's', 'p', 'P', 'X', 'D', '<', '>']
linestyles = ['dotted', 'dashed', 'dashdot', 'solid', (0, (1, 10)), (0, (1, 1)), (0, (1, 1)), (0, (5, 10)), (0, (5, 5)),
              (0, (5, 1)), (0, (3, 1, 1, 1)), (0, (3, 1, 1, 1, 1, 1))]

# time
data = [[27, 73, 548, 1445, 3055, 5644],
        [33, 81, 449, 1278, 2632, 4805],
        [74, 140, 717, 1834, 3405, 5822],
        [54, 110, 418, 912, 1333, 1830]]

# # f-score
# data = [[78, 78, 77, 86, 84, 75],
#         [70, 71, 74, 77, 86, 90],
#         [90, 91, 85, 92, 91, 91],
#         [91, 91, 90, 93, 92, 92]]

assert (len(labels) == len(data))
for i in range(len(labels)):
    # plt.plot([x for x in range(len(data[i]))], data[i], label=labels[i], marker=marks[i], color=colors[i], linestyle=linestyles[i])
    plt.plot(x, data[i], label=labels[i], marker=marks[i], markersize=5, color=colors[i])
    # plt.plot(x, data[i], label=labels[i], marker=marks[i], color=colors[i], linestyle=linestyles[i])

# plt.yticks(np.arange(0, 1 + 0.1, 0.1))
plt.xlabel('Node-Nums', fontsize=14)
plt.ylabel('TIME-S', fontsize=14)
plt.ylim(0, 6000)
y_ticks = np.arange(0, 7000, 1000)
plt.tick_params(direction='in')

plt.yticks(y_ticks)
plt.legend(labels=labels, bbox_to_anchor=(0.25, 0.70), loc='lower right')
# plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), ncol=4, frameon=False, fontsize=8)
plt.tight_layout()
plt.show()
# plt.savefig('lfr_time.png', dpi=750)
# plt.savefig('lfr_time.pdf')
'''
import numpy as np
import matplotlib.pyplot as plt

# plt.style.use('seaborn-darkgrid')

x = ['100', '200', '400', '600', '800', '1000']
labels = ['SSCF', 'LRSCD', 'GBDR', 'SBDR']
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
marks = ['o', 's', '^', 'D']
linestyles = ['-', '--', '-.', ':']

data = [[27, 73, 548, 1445, 3055, 5644],
        [33, 81, 449, 1278, 2632, 4805],
        [74, 140, 717, 1834, 3405, 5822],
        [54, 110, 418, 912, 1333, 1830]]

assert (len(labels) == len(data))
for i in range(len(labels)):
    plt.plot(x, data[i], label=labels[i], marker=marks[i], markersize=7, color=colors[i], linestyle=linestyles[i], linewidth=1.5)

plt.xlabel('Number of nodes', fontsize=14)
plt.ylabel('Time (s)', fontsize=14)
plt.ylim(0, 6000)
y_ticks = np.arange(0, 7000, 1000)
plt.tick_params(direction='in', labelsize=12)

plt.yticks(y_ticks)
plt.legend(labels=labels, bbox_to_anchor=(0.25, 0.70), loc='lower right', fontsize=12)
# plt.grid(True)
plt.tight_layout()
plt.show()
