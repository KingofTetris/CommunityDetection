import numpy as np
import matplotlib.pyplot as plt
from sklearn import manifold, datasets
from sklearn import datasets
from openTSNE import TSNEEmbedding
from openTSNE import TSNE
from openTSNE.affinity import PerplexityBasedNN
from openTSNE import initialization
import numpy as np
import matplotlib.pyplot as plt

import numpy as np
import matplotlib.pyplot as plt
from sklearn import manifold, datasets


def test():
    digits = datasets.load_digits(n_class=6)
    X, y = digits.data, digits.target
    n_samples, n_features = X.shape

    '''显示原始数据'''
    n = 20  # 每行20个数字，每列20个数字
    img = np.zeros((10 * n, 10 * n))
    for i in range(n):
        ix = 10 * i + 1
        for j in range(n):
            iy = 10 * j + 1
            img[ix:ix + 8, iy:iy + 8] = X[i * n + j].reshape((8, 8))
    plt.figure(figsize=(8, 8))
    plt.imshow(img, cmap=plt.cm.binary)
    plt.xticks([])
    plt.yticks([])
    plt.show()
    '''t-SNE'''
    tsne = manifold.TSNE(n_components=2, init='pca', random_state=501)
    X_tsne = tsne.fit_transform(X)

    print("Org data dimension is {}.Embedded data dimension is {} ".format(X.shape[-1], X_tsne.shape[-1]))

    '''嵌入空间可视化'''
    x_min, x_max = X_tsne.min(0), X_tsne.max(0)
    X_norm = (X_tsne - x_min) / (x_max - x_min)  # 归一化
    plt.figure(figsize=(8, 8))
    for i in range(X_norm.shape[0]):
        plt.text(X_norm[i, 0], X_norm[i, 1], str(y[i]), color=plt.cm.Set1(y[i]),
                 fontdict={'weight': 'bold', 'size': 9})
    plt.xticks([])
    plt.yticks([])
    plt.show()


def draw_tsne(X, y):
    n_samples, n_features = X.shape
    '''t-SNE'''
    tsne = manifold.TSNE(n_components=2, init='pca', random_state=501)
    X_tsne = tsne.fit_transform(X)

    print("Org data dimension is {}.Embedded data dimension is {} ".format(X.shape[-1], X_tsne.shape[-1]))

    '''嵌入空间可视化'''
    x_min, x_max = X_tsne.min(0), X_tsne.max(0)
    X_norm = (X_tsne - x_min) / (x_max - x_min)  # 归一化
    plt.figure(figsize=(9, 9))

    for i in range(X_norm.shape[0]):
        plt.text(X_norm[i, 0], X_norm[i, 1], str(y[i]), color=plt.cm.Set1(y[i]),
                 fontdict={'weight': 'bold', 'size': 11})
    plt.xticks([])
    plt.yticks([])
    plt.show()


def draw_optsne():
    iris = datasets.load_iris()
    x, y = iris["data"], iris["target"]
    tsne = TSNE(
        perplexity=30,
        n_iter=50,
        metric="euclidean",
        n_jobs=8,
        random_state=42,
    )
    embedding = tsne.fit(x)
    # utils.plot(embedding, y, colors=utils.MOUSE_10X_COLORS)\


if __name__ == "__main__":
    test()
