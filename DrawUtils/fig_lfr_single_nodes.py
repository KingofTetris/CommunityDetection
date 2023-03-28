#国哥写的
'''
import numpy as np
import matplotlib.pyplot as plt

x = ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9']
labels = ['SSCF', 'LRSCD', 'GBDR', 'SBDR']
colors = ['red', 'orange', 'blue', 'green', 'hotpink', 'turquoise', 'saddlebrown', 'yellowgreen', 'deepskyblue',
          'slategrey']
marks = ['o', 'v', '*', 's', 'p', 'P', 'X', 'D', '<', '>']
linestyles = ['dotted', 'dashed', 'dashdot', 'solid', (0, (1, 10)), (0, (1, 1)), (0, (1, 1)), (0, (5, 10)), (0, (5, 5)),
              (0, (5, 1)), (0, (3, 1, 1, 1)), (0, (3, 1, 1, 1, 1, 1))]
# 1001 small communities
# nmi
data = [[100, 96, 93, 80, 55, 30, 18, 14, 12],
        [100, 99, 98, 92, 60, 36, 20, 16, 15],
        [100, 100, 98, 92, 70, 40, 24, 18, 16],
        [100, 100, 98, 92, 70, 40, 23, 18, 17]]

# mod
# data = [[80, 63, 48, 31, 18, 13, 10, 10, 11],
#         [80, 63, 49, 37, 20, 13, 9, 9, 10],
#         [80, 65, 50, 38, 24, 15, 14, 13, 13],
#         [80, 65, 50, 38, 24, 16, 15, 13, 13]]

#把data的值除以100
for i in range(len(data)):
    for j in range(len(data[i])):
        data[i][j] /= 100

assert (len(labels) == len(data))
for i in range(len(labels)):
    # plt.plot([x for x in range(len(data[i]))], data[i], label=labels[i], marker=marks[i], color=colors[i], linestyle=linestyles[i])
    plt.plot(x, data[i], label=labels[i], marker=marks[i], color=colors[i], linestyle=linestyles[i])
plt.xlabel('NMI', fontsize=14)
plt.ylabel('Q', fontsize=14)
plt.ylim(0, 1.1)
y_ticks = np.arange(0, 1.1, 0.1)
plt.tick_params(direction='in')
plt.yticks(y_ticks)
# plt.legend(handles = [l1, l2,], labels = ['a', 'b'], loc = 'best')
plt.legend(labels=labels, bbox_to_anchor=(0.03, 0.05), loc='lower left')
plt.tight_layout()
plt.show()
# plt.savefig('lfr_1001_q.pdf')

#下面是GPT画的
'''

'''
import numpy as np
import matplotlib.pyplot as plt

# Data
x = ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9']
labels = ['SSCF', 'LRSCD', 'GBDR', 'SBDR']
colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3']
marks = ['o', 'v', '*', 's', 'p', 'P', 'X', 'D', '<', '>']
linestyles = ['dotted', 'dashed', 'dashdot', 'solid', (0, (1, 10)), (0, (1, 1)), (0, (1, 1)), (0, (5, 10)), (0, (5, 5)),
              (0, (5, 1)), (0, (3, 1, 1, 1)), (0, (3, 1, 1, 1, 1, 1))]
data = [[100, 96, 93, 80, 55, 30, 18, 14, 12],
        [100, 99, 98, 92, 60, 36, 20, 16, 15],
        [100, 100, 98, 92, 70, 40, 24, 18, 16],
        [100, 100, 98, 92, 70, 40, 23, 18, 17]]
for i in range(len(data)):
    for j in range(len(data[i])):
        data[i][j] /= 100

# Plot
fig, ax = plt.subplots(figsize=(7, 4), dpi=120)
for i in range(len(labels)):
    ax.plot(x, data[i], label=labels[i], marker=marks[i], color=colors[i], linestyle=linestyles[i])

# Style
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.tick_params(axis='both', direction='in', length=4, width=1, labelsize=12)
ax.yaxis.grid(ls='--', alpha=0.7)
ax.set_ylim(0, 1.1)
ax.set_yticks(np.arange(0, 1.1, 0.1))
ax.legend(labels=labels, bbox_to_anchor=(0.02, 1.02), loc='lower left', ncol=2, frameon=False, fontsize=12)

# Labels
ax.set_xlabel('Overlap Ratio', fontsize=14, labelpad=10)
ax.set_ylabel('NMI', fontsize=14, labelpad=10)
fig.suptitle('LFR Benchmark', fontsize=18)

plt.tight_layout()
plt.show()
'''
import numpy as np
import matplotlib.pyplot as plt

# Data
x = ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9']
labels = ['SSCF', 'LRSCD', 'GBDR', 'SBDR']
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
linestyles = ['-', '--', ':', '-.']
data = [[100, 96, 93, 80, 55, 30, 18, 14, 12],
        [100, 99, 98, 92, 60, 36, 20, 16, 15],
        [100, 100, 98, 92, 70, 40, 24, 18, 16],
        [100, 100, 98, 92, 70, 40, 23, 18, 17]]
for i in range(len(data)):
    for j in range(len(data[i])):
        data[i][j] /= 100

# Plot
fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
for i in range(len(labels)):
    ax.plot(x, data[i], label=labels[i], color=colors[i], linestyle=linestyles[i])

# Style
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.tick_params(axis='both', direction='in', length=4, width=1, labelsize=12)
ax.yaxis.grid(ls='--', alpha=0.7)
ax.set_ylim(0, 1.1)
ax.set_yticks(np.arange(0, 1.1, 0.1))
ax.legend(labels=labels, bbox_to_anchor=(0.02, 1.02), loc='lower left', ncol=2, frameon=False, fontsize=12)

# Labels
ax.set_xlabel('Overlap Ratio', fontsize=14, labelpad=10)
ax.set_ylabel('Normalized Mutual Information', fontsize=14, labelpad=10)
fig.suptitle('LFR Benchmark', fontsize=18)

plt.tight_layout()
plt.show()
