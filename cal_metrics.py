import networkx as nx
import csv

from networkx.algorithms.community.quality import modularity, performance  #quality里面有"coverage", "modularity", "performance"3个指标
from communities.visualization import draw_communities
from sklearn import metrics
from sklearn.metrics import normalized_mutual_info_score as NMI
import numpy as np
from networkx.algorithms.community import is_partition
import algorithm.CPM as CPM
import algorithm.LPA as LPA
from algorithm.Louvain import Louvain
import algorithm.SCAN as SCAN
import leidenalg as leiden
import os



'''
这个程序挺有用的，可以自己写个程序写community.dat就可以生成gml文件可视化了

基于LFR——benchmark生成后的数据进行处理，生成预览及GML文件 其实不仅仅是做LFR，对算法的分类结果也可以做到可视化。

参考文献： A. Lancichinetti, S.Fortunato, F. Radicchi, Benchmark graphsfor testing community detection algorithms, Phys. Rev. E 78 (2008) 046-110.

'''

#计算十次度量 LFR网络
def compute_metrics_LFR_network(dataset_name):
    edge_file = './data/LFR_benchmark/LFR_test/' + dataset_name + '/'  + dataset_name + '.dat'
    community_file = './data/LFR_benchmark/LFR_test/'+ dataset_name + '/'  + dataset_name + '_com.dat'
    algorithm_community_file_path = './data/algorithm_communities/nash_algorithm/' + dataset_name + '/'
    file_list = os.listdir(algorithm_community_file_path)
    #把每个文件都算一次
    flag = 1
    for item in file_list:
        #print(item)
        algorithm_file_path = algorithm_community_file_path + item
        read_LFR(edge_file,community_file,algorithm_file_path,flag)
        flag = flag + 1

#计算十次度量 真实数据集
def compute_metrics_real_network(dataset_name):
    community_file = './data/real_network/' + dataset_name + '_com.dat'
    edge_file = './data/real_network/' + dataset_name + '.dat'
    # algorithm_community_file_path = './data/algorithm_communities/nash_improvement/' + dataset_name + '/'
    algorithm_community_file_path = './data/algorithm_communities/nash_algorithm/' + dataset_name + '/'
    file_list = os.listdir(algorithm_community_file_path) #文件夹
    #把每个文件都算一次
    flag = 1
    for item in file_list:#遍历文件夹下的所有文件
        #print(item)
        algorithm_file_path = algorithm_community_file_path + item
        try:
            read_LFR(edge_file,community_file,algorithm_file_path,flag) #暂时只有比较NMI
        except Exception as e:
            print(e)
            print("出现异常,开始计算下一个实验结果")
            flag = flag + 1 #写在这里是因为continue后面的语句不会执行
            continue #如果长度不匹配，继续下一个文件夹
        flag = flag + 1



def read_LFR(edge_file_path,community_file_path,algorithm_file_path,flag):
    G = nx.Graph()
    # 定义边文件和社团文件
    # edge_file = './data/real_network/dolphins.dat'
    # community_file = './data/real_network/dolphins_com.dat'
    edge_file = edge_file_path
    community_file = community_file_path
    algorithm_community_file = algorithm_file_path
    # community_file = './data/real_network/polblogs_com.dat'
    # edge_file = './data/real_network/polblogs.dat'
    # community_file = './data/real_network/polblogs_com.dat'
    #algorithm_community_file = './data/algorithm_communities/nash_algorithm/nashOverlappingCommunities100_dolphins.dat'
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

    if flag==1: #第一次打印一下网络信息
        print(nx.info(G))
    print('-----------------------------第' + str(flag) + '次-----------------------------------')
    # # 绘图
    #draw_communities(G, partition)
    # # 另存为gml文件，可以注册NEUSNCP账号后上传gml文件，使用 https://neusncp.com/api/cd 的可视化工具验证
    #nx.write_gml(G, 'data/res/LFR/node3000/true_node3000.gml')


    #真实社区分布 real_com_list
    real_com_list = []
    community_index = 0
    for c in partition:
        community_index = community_index + 1
        for element in c:
            real_com_list.insert(int(element) - 1,community_index)

    # print(len(real_com_list))
    # real_com_list_karate = [1,1,1,1,1,1,1,1,2,2,
    #                 1,1,1,1,2,2,1,1,2,1,
    #                 2,1,2,2,2,2,2,2,2,2,
    #                 2,2,2,2]  #空手道俱乐部真实分区列表

    # 算法社区分布 algorithm_com_partition 有个大问题，真是分区是按1-n排序后读出来的。那么真是分区的社区号一定是相同的。
    # 但是这个B算法，是按照谁先出现，谁的社区号就小来的。导致社区号不一致。可能得人为调整一下。。
    # 比如下面这个 上面的是1号社区，下面的是2号社区。
    # 16 19 36 52 5 22 24 56 25 12 30 46
    # 1 2 3 4 6 7 8 9 10 11 13 14 15 17 18 20 21 23 26 27 28 29 31 32 33 34 35 37 38 39 40 41 42 43 44 45 47 48 49 50 51 53 54 55 57 58 59 60 61 62
    # 简单说就是谁先出现谁就是小社区。
    #怎么解决这个问题？。先把partition排序一下？确实可以。
    algorithm_com_partition = read_algorithm_community(algorithm_community_file)

    # print("算法分区如下：")
    # for c in algorithm_com_partition:
    #     print(c)

    algorithm_com_list = [] #实际上分不分序号都无所谓。用分区直接比较就行了。
    community_index = 0
    for c in algorithm_com_partition:
        community_index = community_index + 1
        for element in c:
            algorithm_com_list.insert(int(element) - 1,community_index)
    # print(len(algorithm_com_list))

    # print('两个分区文件的长度对比，有的分区会出现重叠社区，很怪')
    # print(len(real_com_list))
    # print(len(algorithm_com_list))  # 为什么算法分区列表多了两个值？1490 1492？？？？
    # print("真实与算法标签对比:")
    # print(real_com_list)
    # print(algorithm_com_list)
    # # 计算一下模块度
    print("真实分区模块度:" + str(modularity(G, partition)))
    #print(is_partition(G,algorithm_com_partition))
    try:
        print("算法分区模块度:" + str(modularity(G,algorithm_com_partition)))
    except Exception as err: #抛出数量不一致的异常
        print('An exception occured:' + str(err))
    #直接用sklearn 计算NMI

    #建议直接写在文件里面，不要再写到控制台了
    print("本次算法分区NMI的值为:" + str(NMI(real_com_list,algorithm_com_list)))
    print("本次算法分区ARI的值为:" + str(metrics.adjusted_rand_score(real_com_list,algorithm_com_list)))




#根据文件返回算法的分区
def read_algorithm_community(filepath):
    # algorithm_community_file = './data/algorithm_communities/nash_algorithm/nashOverlappingCommunities100_dolphins.dat'
    algorithm_community_file = filepath
    partition = []
    temp = []
    with open(algorithm_community_file, 'r') as fp:
        for line in fp.readlines():  ##readlines(),函数把所有的行都读取进来；
            # temp = list(line.strip().split('\t'))  ##删除行后的换行符并按\t分割，temp 就是每行的内容啦
            temp = list(line.strip().split(' '))  ##删除行后的换行符并按\t分割，temp 就是每行的内容啦
            partition.append(temp)
            #temp = [] #读完一行，把temp赋值为新的空列表
    # for c in partition:
    #     print(c)
    #partition.sort() #排不排序无所谓。
    return partition

if __name__ == '__main__':
    #read_LFR()
    fnamelist = ['karate','dolphins','football','polbooks','polblogs'] #这个顺序是按照节点数来的

    #异常在函数里面处理了，在这外面的for 不会出现异常 没必要try exception
    for fname in fnamelist:
        compute_metrics_real_network(fname)
        print("-------------------我是分割线--------------------------")
        print("\n\n\n")
