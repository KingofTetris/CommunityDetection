import networkx as nx
import csv
from networkx.algorithms.community.quality import modularity, performance  #quality里面有"coverage", "modularity", "performance"3个指标
from communities.visualization import draw_communities
from sklearn.metrics import normalized_mutual_info_score as NMI
import numpy as np



'''
这个程序挺有用的，可以自己写个程序写community.dat就可以生成gml文件可视化了

基于LFR——benchmark生成后的数据进行处理，生成预览及GML文件 其实不仅仅是做LFR，对算法的分类结果也可以做到可视化。

参考文献： A. Lancichinetti, S.Fortunato, F. Radicchi, Benchmark graphsfor testing community detection algorithms, Phys. Rev. E 78 (2008) 046-110.

'''


def read_LFR():
    G = nx.Graph()
    # 定义边文件和社团文件
    edge_file = '../data/LFR_benchmark/LFR_test/LFR_node1000/network.dat'
    community_file = './data/LFR_benchmark/LFR_test/LFR_node1000/community.dat'
    # edge_file = './data/real_network/football.dat'
    # community_file = './data/real_network/football_com.dat'
    # 读取数据，并以tab键分割
    data = csv.reader(open(edge_file, 'r'), delimiter='\t')
    # for d in data: #每个d都是一个列表
    #     for node in d:
    #         print(node)
    # 加边
    edges = [d for d in data]
    #print(edges)
    # for edge in edges:
    #     print(edge)
    G.add_edges_from(edges) #add_edges_from可以直接添加列表
    # # 读社团
    community = csv.reader(open(community_file, 'r'), delimiter='\t')
    #print(community)
    #标记社区
    labels = {d[0]:d[1] for d in community}  #labels {'1':'4','2':'2',............}生成这样的字典
    for n in G.nodes():
        G.nodes[n]['group'] = labels[n] #给节点标记所属的社区
    groups = set(labels.values()) #节点的所属社区集合 用set去重 如果不去重 那就128个节点全算一次
    nodes = labels.keys() #节点的序号
    partition = [] #partition是一个嵌套列表。列表里面的元素也是列表。
    temp = []
    for g in groups:
        for n in nodes:
            if labels[n] == g:
                temp.append(n) #如果所属社区是1就添加进去
        partition.append(temp)
        temp=[]
    # for c in partition:  #为什么也是128？？？？？因为一开始没用set去重groups
    #     print(c)
    #partition = [ [n for n in nodes if labels[n] == g] for g in groups ] #还有这种操作 但为什么有128行？？
    print(nx.info(G))
    # # 绘图
    #draw_communities(G, partition)
    # # 另存为gml文件，可以注册NEUSNCP账号后上传gml文件，使用 https://neusncp.com/api/cd 的可视化工具验证
    #nx.write_gml(G, 'data/res/LFR/node1000.gml')
    # # 计算一下模块度
    print(modularity(G, partition))
    #partition就是真实分区。
    algri_partition = []
if __name__ == '__main__':
    read_LFR()