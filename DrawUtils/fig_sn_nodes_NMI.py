import numpy as np
import matplotlib.pyplot as plt

x = ['adjnoun', 'karate', 'dolphins', 'football', 'polbooks', 'network19']
labels = ['GN', 'LFM', 'Louvain', 'SLPA', 'SSCF', 'LRSCD', 'BDR-B', 'BDR-Z', 'CBDR-B', 'CBDR-Z']
colors = ['red', 'orange', 'blue', 'green', 'hotpink', 'turquoise', 'saddlebrown', 'yellowgreen', 'deepskyblue',
          'slategrey']
marks = ['o', 'v', '*', 's', 'p', 'P', 'X', 'D', '<', '>']
linestyles = ['solid', 'dotted', 'dashed', 'dashdot', (0, (1, 10)), (0, (1, 1)), (0, (1, 1)), (0, (5, 10)), (0, (5, 5)),
              (0, (5, 1)), (0, (3, 1, 1, 1)), (0, (3, 1, 1, 1, 1, 1))]
data = [[0.1488, 0.5798, 0.5541, 0.8788, 0.5645, 1.0],
        [0.0119, 0.6021, 0.4795, 0.9031, 0.4687, 1.0],
        [0.0057, 0.6021, 0.4557, 0.8903, 0.5156, 1.0, ],
        [0.0, 0.5801, 0.7358, 0.8456, 0.5561, 1.0],
        [0.0225, 0.8365, 0.8888, 0.9191, 0.5274, 1.0],
        [0.0036, 0.5106, 0.8888, 0.8656, 0.5871, 1.0],
        [0.0155, 0.7329, 0.8888, 0.9304, 0.5843, 1.0],
        [0.0205, 0.6459, 0.8888, 0.9305, 0.5843, 1.0],
        [0.2425, 1.0, 0.8888, 0.9304, 0.5929, 1.0],
        [0.2177, 1.0, 0.8888, 0.9308, 0.5929, 1.0]]
assert (len(labels) == len(data))
for i in range(len(labels)):
    # plt.plot([x for x in range(len(data[i]))], data[i], label=labels[i], marker=marks[i], color=colors[i], linestyle=linestyles[i])
    plt.plot(x, data[i], label=labels[i], marker=marks[i], color=colors[i], linestyle=linestyles[i])
plt.yticks(np.arange(0, 1 + 0.1, 0.1))
plt.xlabel('DataSet', fontsize=14)
plt.ylabel('NMI', fontsize=14)
plt.ylim(0, 1)
plt.tick_params(direction='in')
# plt.legend(loc=8, mode='expand', ncol=4)
plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False, fontsize=14)
plt.tight_layout()
plt.show()
# plt.savefig('2fig_sn_nodes_NMI.pdf')
