import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def draw_coff(mat,path=''):
    # plt.matshow(mat, cmap=plt.cm.Blues)
    sns.heatmap(mat, cmap='GnBu',xticklabels=False,yticklabels=False)

    plt.show()
    # plt.savefig(path+'.pdf',bbox_inches="tight")

    cax = plt.gcf().axes[-1]
    cax.tick_params(labelsize=10)


if __name__ == '__main__':
    mat = np.arange(0, 100).reshape(10, 10)
    draw_coff(mat)
