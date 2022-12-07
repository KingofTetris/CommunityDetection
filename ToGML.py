import os

import networkx as nx
import csv


'''
这个程序挺有用的，可以自己写个程序写community.dat就可以生成gml文件可视化了

基于LFR——benchmark生成后的数据进行处理，生成预览及GML文件 其实不仅仅是做LFR，对算法的分类结果也可以做到可视化。

参考文献： A. Lancichinetti, S.Fortunato, F. Radicchi, Benchmark graphsfor testing community detection algorithms, Phys. Rev. E 78 (2008) 046-110.

'''
def preWork(filepath):
    read_algorithm_community_and_save_community_dat(filepath)

def toGML():
    G = nx.Graph()
    # 定义边文件和社团文件
    edge_file = './data/LFR_benchmark/LFR_test/LFR_node3000/network.dat'
    #community_file = './data/real_network/polblogs_com.dat'
    community_file = './data/LFR_benchmark/LFR_test/LFR_node3000/community.dat'
    # edge_file = './data/real_network/football.dat'
    # community_file = './data/real_network/football_com.dat'
    # 读取数据，并以tab键分割
    data = csv.reader(open(edge_file, 'r'), delimiter='\t')

    #读取数据，以空格分割
    #data = csv.reader(open(edge_file, 'r'), delimiter=' ')
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
    # algorithm_community_handle = open(algorithm_community_file, 'r')
    #print(algorithm_community)
    #print(community)
    #标记社区

    labels = {d[0]:d[1] for d in community}  #labels {'1':'4','2':'2',............}生成这样的字典
    for n in G.nodes():
        G.nodes[n]['group'] = labels[n] #给节点标记所属的社区
    set_groups = set(labels.values()) #节点的所属社区集合 用set去重 如果不去重 那就128个节点全算一次 问题是你用set会打乱社区的顺序！
    groups = list(set_groups) #所以把他转回list然后进行sort
    groups.sort() #这样就可以保证后面要用到NMI的计算里面，真实社区的编号一定是从1-n排序。

    nodes = labels.keys() #节点的序号
    partition = [] #partition是一个嵌套列表。列表里面的元素也是列表。
    temp = []
    for g in groups:
        for n in nodes:
            if labels[n] == g:
                temp.append(n) #如果所属社区是g就添加进去
        partition.append(temp)
        temp=[]

    #partition.sort() #先partition排序一下(按长度由大到小排序)
    # print("真实分区如下：")
    # for c in partition:  #为什么也是128？？？？？因为一开始没用set去重groups
    #     print(c)
    #partition = [ [n for n in nodes if labels[n] == g] for g in groups ] #还有这种操作 但为什么有128行？？

    print(nx.info(G))
    ## 绘图
    #draw_communities(G, partition)
    # # 另存为gml文件，可以注册NEUSNCP账号后上传gml文件，使用 https://neusncp.com/api/cd 的可视化工具验证
    nx.write_gml(G, 'data/res/LFR/node3000/nash_080_node3000.gml') #把图存为gml文件

#根据partition文件返回算法的分区
def read_algorithm_community_and_save_community_dat(community_filepath):
    # algorithm_community_file = './data/algorithm_communities/nash_algorithm/nashOverlappingCommunities100_dolphins.dat'
    algorithm_community_file = community_filepath
    partition = [] #[1,1,1,1,4,4,4,5,6,6,6,6.................]
    temp = []
    with open(algorithm_community_file, 'r') as fp:
        for line in fp.readlines():  ##readlines(),函数把所有的行都读取进来；
            # temp = list(line.strip().split('\t'))  ##删除行后的换行符并按\t分割，temp 就是每行的内容啦
            temp = list(line.strip().split(' '))  ##删除行后的换行符并按\t分割，temp 就是每行的内容啦
            partition.append(temp)
            #temp = [] #读完一行，把temp赋值为新的空列表

    # print(community_filepath.split('/')[-1].split('.')[0].split('_'))  #nashOverlappingCommunities100_dolphins
    # print( (community_filepath.split('/')[-1].split('.')[0].split('_'))[1]  )  #dolphins
    #根据partition给个xxx_com文件
    name = 'nash_algorithm_' + community_filepath.split('/')[-1].split('.')[0].split('_')[1] + '_com.dat'
    save_gml_path = './data/algorithm_communities/nash_algorithm_communityFile/' + name
    with open(save_gml_path, 'w') as fp:
        index = 0
        for community in partition:
            index = index + 1
            for c in community:
                fp.write(str(c) + "\t" + str(index))
                fp.write("\n")


if __name__ == '__main__':
    filepath = './data/algorithm_communities/nash_algorithm/nashOverlappingCommunities100_LFR_node3000.dat'
    #preWork(filepath) #先生成com.dat文件，有了就没必要了。
    toGML()