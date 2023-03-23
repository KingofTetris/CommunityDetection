import numpy as np
import matplotlib.pyplot as plt

x = ['100', '200', '400', '600', '800', '1000']
labels = ['SSCF', 'LRSCD', 'GBDR', 'SBDR']
colors = ['red', 'orange', 'blue', 'green', 'hotpink', 'turquoise', 'saddlebrown', 'yellowgreen', 'deepskyblue',
          'slategrey']
marks = ['o', 'v', '*', 's', 'p', 'P', 'X', 'D', '<', '>']
linestyles = ['dotted', 'dashed', 'dashdot', 'solid', (0, (1, 10)), (0, (1, 1)), (0, (1, 1)), (0, (5, 10)), (0, (5, 5)),
              (0, (5, 1)), (0, (3, 1, 1, 1)), (0, (3, 1, 1, 1, 1, 1))]
data = [[81, 73, 77, 79, 82, 81],
        [90, 86, 80, 84, 85, 91],
        [91, 91, 85, 86, 87, 92],
        [93, 91, 87, 88, 88, 92]]

# mod
data = [[33, 35, 29, 32, 30, 32],
        [33, 35, 31, 33, 33, 35],
        [33, 35, 31, 34, 35, 36],
        [33, 35, 32, 34, 35, 37]]

# # f-score
# data = [[78, 78, 77, 86, 84, 75],
#         [88, 87, 82, 90, 86, 90],
#         [90, 91, 85, 92, 91, 91],
#         [91, 91, 90, 93, 92, 92]]

assert (len(labels) == len(data))
for i in range(len(labels)):
    # plt.plot([x for x in range(len(data[i]))], data[i], label=labels[i], marker=marks[i], color=colors[i], linestyle=linestyles[i])
    plt.plot(x, data[i], label=labels[i], marker=marks[i], color=colors[i], linestyle=linestyles[i])
plt.yticks(np.arange(0, 1 + 0.1, 0.1))
plt.xlabel('Node-Nums', fontsize=14)
plt.ylabel('Q', fontsize=14)
plt.ylim(0, 50)
y_ticks = np.arange(0, 60, 10)
plt.tick_params(direction='in')
plt.yticks(y_ticks)
plt.legend(labels=labels, bbox_to_anchor=(0.98, 0.05), loc='lower right')
# plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False, fontsize=14)
plt.tight_layout()
plt.show()
# plt.savefig('lfr_total_mod.png', dpi=750)
