# -*- coding: utf-8 -*-
import math
from collections import defaultdict
from sklearn import metrics
from networkx.algorithms.community.quality import modularity # 模块度 modularity(G,partition)
import networkx as nx
import random

'''

'''
#TODO 而且这个程序把计算度量值都放在算法里了，实在是不太合理，后面有时间改一改

#TODO 目前是非重叠版本
class non_overlap_game:
    #构造函数
    def __init__(self, filepath='', fname = ''):
        '''
        Constructor
        '''
        print("-------------------------")
        print("init begin:")
        self.filepath = filepath
        self.store_graphlist(fname)
        print ("processing %s" % self.filepath)
        print ("init done")
        print ("-------------------------")



    # Compute the intimacy coefficient of two node
    #  u->v u对v的吸引力 因为参考现实中两个人的亲密度其实是不同的
    # 所以我们设置两个方向的吸引力，目前的区别仅仅是采用了各自的度
    #目前最好的，还是原始AA*di的版本
    def simintimacy(self,u,v):
        #如果u==v 防止有环
        #自己和自己亲密度当然是最大
        #直接返回自己的度
        if(u == v):
            return [self.deg[u],self.deg[v]]

        set_v = set(self.G.neighbors(v))
        set_u = set(self.G.neighbors(u))
        comm_neighbors = set_v & set_u # u和v的公共邻居
        # #TODO 考虑到底要不要加上去
        # # # 但是AA指数对于直接连边的节点对亲密度居然是0，这个时候我们要特殊处理一下节点对有直接连边 但是没有公共邻居的情况
        # if len(comm_neighbors) == 0 and self.G.edges(u,v) is not None:
        #     # self.specialedge_num = self.specialedge_num + 1
        #     # print("这样的边有:" + str(self.specialedge_num) + "条")
        #     # #两者虽然没有公共邻居，但是直接连边的关系让亲密度也不会很低
        #     # #TODO 我们暂时让这个节点对的亲密度设为这条边的权重为两个节点的度数之和的一半
        #     # # 实验后看结果，这样处理了的区别是，dolphins NMI从0.48变大到0.51 但是其他数据集的NMI都变小，尤其karate直接小一半。
        #     avg = (self.deg[u] + self.deg[v]) / 2
        #     # return[avg,avg]
        #     #把这条边的权重设为度的一半，用1除以他们度的乘积衡量这条边的重要性
        #     return[avg/(self.deg[u] * self.deg[v]),avg/(self.deg[u] * self.deg[v])]

        #AA指数
        AA_uv = 0.0

        #遍历公共邻居 另外 如果能到这一步，那么neighbors的长度至少是1，也就是一个公共邻居，应该不可能存在neg的度为1的情况
        #如果comm_neighbors是空的，那么他们的AA指数就是初始的0
        #但问题在于我算亲密度的地方都是和邻居算，就算他们没有共同邻居，他们的直接连边也是很重要的。
        #不能直接弄成0吧？
        for neg in comm_neighbors:
            #获得邻居的度
            deg_neg = self.deg[neg]
            #计算AA math.log默认以e为底也就是ln
            #按理来说公共邻居的度至少是2，不知道为什么会出现1，可能数据集有误，这里处理一下。
            # 防止deg_neg为1造成除0异常
            #搞清楚了，不是因为deg_neg等于1引发的错，是polblogs数据集1260号节点是一个环
            #(1260，1260)的邻居必然有那个1259(度为1的节点)
            # if deg_neg == 1:
            #     print("出错的邻居对是:" + str(u) + "_"  +str(v))
            #     print("出错的公共邻居是节点" + str(neg))
            #     continue #如果为1 跳过这个节点
            AA_uv = AA_uv + (1 / (math.log(deg_neg)))

        # if(self.G.edges(u,v) is not None and AA_uv == 0): #其实前面判断边是否存在没啥必要，因为我算亲密度只和邻居算。 先加上吧，万一以后全算呢
        #     #这个公式的含有是，分子的1是他们的直接连边
        #     #分母是他们度的乘积，如果他们的乘积越大，那么他们的不同朋友就越多，那么这条直接连边就越不重要
        #     #或者换句话说，这个公式就是在算这条边的权重。他们的相似度就是这条边的权重
        #     # return[1/math.sqrt(self.deg[u] * self.deg[v]),1/math.sqrt(self.deg[u] * self.deg[v])]
        #     return[1/(self.deg[u] * self.deg[v]),1/(self.deg[u] * self.deg[v])]

        #吸引力
        init_u_to_v = AA_uv * self.deg[u]
        init_v_to_u = AA_uv * self.deg[v]
        #返回u对v 和v对u的亲密度
        return [init_u_to_v,init_v_to_u]

    '''
    下面这些只是节点相似度进行了修改，把AA指数换成其他，对不同亲密度指标的尝试(已经做了实验_2023_03_09)
    都没有取得明显更好的效果
    '''
    #平衡AA指数 AAE
    #该公式在计算节点相似度时，将节点度数的平方根作为加权系数，对AA指数进行平衡，
    # 使得度数较大的节点不会对节点相似度指标造成过大的影响，从而更加合理地反映节点之间的相似度。
    '''
    def simintimacy(self,u,v):
        set_v = set(self.G.neighbors(v))
        set_u = set(self.G.neighbors(u))
        neighbors = set_v & set_u # u和v的公共邻居

        # 但是AA指数对于直接连边的节点对亲密度居然是0，这个时候我们要特殊处理一下节点对有直接连边 但是没有公共邻居的情况
        if len(neighbors) == 0 and self.G.edges(u,v) is not None:
            #两者虽然没有公共邻居，但是直接连边的关系让亲密度也不会很低
            #TODO 我们暂时让这个节点对的亲密度设为这条边的权重为两个节点的度数之和的一半
            # 实验后看结果，这样处理了也没有太大差别。
            avg = (self.deg[u] + self.deg[v]) / 2
            return[avg,avg]

        #AA指数
        AA_uv = 0.0

        #遍历公共邻居 另外 如果能到这一步，那么neighbors的长度至少是1，也就是一个公共邻居，应该不可能存在neg的度为1的情况
        for neg in neighbors:
            #获得邻居的度
            deg_neg = self.deg[neg]
            #计算AA math.log默认以e为底也就是ln
            #按理来说公共邻居的度至少是2，不知道为什么会出现1，可能数据集有误，这里处理一下。
            # 防止deg_neg为1造成除0异常
            if deg_neg == 1:
                continue #如果为1 跳过这个节点
            AA_uv = AA_uv + (1 / (math.log(deg_neg)))

        #有了AA_uv以后多加一个权重系数来计算AAE_uv
        AAE_uv = AA_uv/ math.sqrt(self.deg[u] * self.deg[v])

        init_u_to_v = AAE_uv * self.deg[u]
        init_v_to_u = AAE_uv * self.deg[v]
        #返回u对v 和v对u的亲密度
        return [init_u_to_v,init_v_to_u]
    '''
    ##RA版本
    '''
    def simintimacy(self,u,v):

        set_v = set(self.G.neighbors(v))
        set_u = set(self.G.neighbors(u))
        neighbors = set_v & set_u # u和v的公共邻居

        # 但是RA指数对于直接连边的节点对亲密度也是0，这个时候我们要特殊处理一下节点对有直接连边 但是没有公共邻居的情况
        if len(neighbors) == 0 and self.G.edges(u,v) is not None:
            #两者虽然没有公共邻居，但是直接连边的关系让亲密度也不会很低
            #TODO 我们暂时让这个节点对的亲密度设为这条边的权重为两个节点的度数之和的一半
            # 实验后看结果，这样处理了也没有太大差别。
            avg = (self.deg[u] + self.deg[v]) / 2
            return[avg,avg]

        #RA指数
        RA_uv = 0.0

        #遍历公共邻居 另外 如果能到这一步，那么neighbors的长度至少是1，也就是一个公共邻居，应该不可能存在neg的度为1的情况
        for neg in neighbors:
            #获得邻居的度
            deg_neg = self.deg[neg]
            #计算AA math.log默认以e为底也就是ln
            #按理来说公共邻居的度至少是2，不知道为什么会出现1，可能数据集有误，这里处理一下。
            # 防止deg_neg为1造成除0异常
            if deg_neg == 1:
                continue #如果为1 跳过这个节点
            RA_uv = RA_uv + (1 / deg_neg)

        init_u_to_v = RA_uv * self.deg[u]
        init_v_to_u = RA_uv * self.deg[v]
        #返回u对v 和v对u的亲密度
        return [init_u_to_v,init_v_to_u]
    '''
    #simRank版本
    #对于节点度相同的节点，如果它们的邻居不同，那么亲密度值也会不同，
    # 这可能导致一些节点被错误地归入不合适的社区中。为了避免这个问题，可以采用一些更加准确的亲密度指标，比如Katz指标或者SimRank指标。
    '''
    def simRank(self,u,v):
        C = 0.7 #阻尼系数取值(0,1) 一般设置为0.6-0.8
        if u == v:
            return 1
        #因为是无向图那么入邻居就是邻居
        neigh_u = self.G.neighbors(u)
        neigh_v = self.G.neighbors(v)

        simRankValue = 0.0 #初始值

        for temp_v in neigh_v:
            for temp_u in neigh_u:
                #递归计算相似度
                simRankValue = simRankValue + self.simRank(temp_u,temp_v)

        return simRankValue
    '''
    #Jaccard版本
    #Compute the jaccard similarity coefficient of two node
    #两节点的jaccard相似度
    '''
    def simintimacy(self, u, v):
        set_v = set(self.G.neighbors(v))
        set_v.add(v)
        set_u = set(self.G.neighbors(u))
        set_u.add(u)
        jac = len(set_v & set_u) * 1.0 / len(set_v | set_u)    #集合相与取交集，相或取并集。
        return [jac * self.deg[u],jac * self.deg[v]]
    '''
    #Salton(余弦相似度)版本 比AA稍微差一点，但差不太多
    '''
    def simintimacy(self, u, v):
        set_v = set(self.G.neighbors(v))
        set_u = set(self.G.neighbors(u))
        salton = len(set_v & set_u) * 1.0 / math.sqrt(self.deg[u]*self.deg[v])  # 集合相与取交集，相或取并集。
        return [salton * self.deg[u], salton * self.deg[v]]
    '''
    #Sorensen版本 dolphins的比AA好，其他稍差，也差不太多
    '''
    def simintimacy(self, u, v):
        set_v = set(self.G.neighbors(v))
        set_u = set(self.G.neighbors(u))
        sorensen = 2 * len(set_v & set_u) * 1.0 / (self.deg[u] + self.deg[v])  # 集合相与取交集，相或取并集。
        return [sorensen * self.deg[u], sorensen * self.deg[v]]
    '''
    #HP版本 也和AA差不多
    '''
    def simintimacy(self, u, v):
        set_v = set(self.G.neighbors(v))
        set_u = set(self.G.neighbors(u))
        HP = len(set_v & set_u) * 1.0 / min(self.deg[u],self.deg[v])  # 集合相与取交集，相或取并集。
        return [HP * self.deg[u], HP * self.deg[v]]
    '''
    #HD版本 和HP类似，结果和AA也大差不差。
    '''
    def simintimacy(self, u, v):
        set_v = set(self.G.neighbors(v))
        set_u = set(self.G.neighbors(u))
        HD = len(set_v & set_u) * 1.0 / max(self.deg[u], self.deg[v])  # 集合相与取交集，相或取并集。
        return [HD * self.deg[u], HD * self.deg[v]]
    '''

    '''
     # 只去计算在相邻社区c中的邻居节点的亲密度
       for v in self.G.neighbors(u):
           v_community = self.node_community[v]  # 节点v的社区标签
           if (v_community == c): #如果v在社区c中，那么才会计算收益
               list = self.simintimacy(u,v)
               #暂时是非重叠，那community标签就一个 int型不能用len函数
               # paysoff_u = paysoff_u + 1/2 * (list[0] / len(u_community) + list[1] / len(v_community)) * (u_community & v_community)
               paysoff_u = paysoff_u + 1/2 * (list[0] + list[1]) * (u_community & v_community)
       return paysoff_u
    '''

    #收益函数1  U(S_(-i),s_i )=∑_(a_ij=1)〖1/2(〖Intimacy〗_(j→i)/(|s_i|)+〖Intimacy〗_(i→j)/(|s_j|))〗|s_i⋂s_j|
    # 现在问题是检测非重叠社区时，离开社区的效用是0，导致不会有社区选择离开当前社区
    # 典型例子是football网络里面1个社区吞并了3个小社区。
    # 单社区的时候这个utility = 1/2 (I(j->i)/1 + I(i->j)/1)*1 = 1/2 * (I(j->i) + I(i->j))
    def utility_function(self,u,c): # 节点u在社区c中的收益
       paysoff_u = 0
       #计算社区C中的所有节点与u的亲密度累加作为效用函数
       #让他们累加起来作为节点u的效用
       for node in self.G.nodes():
           if self.node_community[node] == c:
               list = self.simintimacy(u,node)
               #现在就是简单的亲密度求和
               #后面可能要考虑一下改进效用函数
               #简单求和简单来说就是让度越大的节点有越高比重，节点只要和那个度大的节点相连接，那么必然会对这个度大的邻居所在社区c产生较大亲密度
               #但问题就在于节点u和这个度大的邻居仅仅只有一条连边，他的其他边连接的节点可能在别的社区，但它因为这个度很大的邻居被硬生生拉进去社区c
               paysoff_u = paysoff_u + 1/2 * (list[0] + list[1])
       return  paysoff_u


    #收益函数2 明明看起来更复杂但这个收益函数比前面的要差
    #gain = 1/2m ∑(i,j) (Aijδ(i,j) - Intimacydidj/2m * |si ∩ sj|  δ(i,j)表示i.j是否有共同标签
    #loss = 1/2m (|si| - 1)
    # def utility_function(self,u,c): # 节点u在社区c中的收益
    #     gain_function = 0
    #     for neigh in self.G.neighbors(u): #Aij = 1
    #         community_neigh = self.node_community[neigh]
    #         community_node = self.node_community[u]
    #         deerta = 0
    #         # δ(i,j)表示i.j是否有共同标签
    #         if community_neigh != community_node:
    #             deerta = 0
    #         else:
    #             deerta = 1
    #         gain_function = gain_function + 1/2 * self.edge_count * \
    #                         (1 * deerta - \
    #                         1/2 * (self.simintimacy(u,neigh)[0] + self.simintimacy(u,neigh)[1]) \
    #                          * self.deg[u] * self.deg[neigh] / 2 * self.edge_count * 1 )
    #                         # * (community_node & community_neigh) ) #正常是要取交集，但是这里单社区，直接数字1就行了
    #     # loss_function = 1/ 2 * self.edge_count * (len(self.node_community[u]) - 1) # 目前做单社区，那不能用len函数，其实就是1 没有损失
    #     loss_function = 0
    #     utility = gain_function - loss_function
    #     return utility
    # 造图,并形成初始社区

    def store_graphlist(self, fname):
        # graph
        self.specialedge_num = 0 #计算一下那些特殊边的数量，节点对没有共同邻居，但是有直接连边
        self.G = nx.Graph()
        self.input_node_community = defaultdict(int)
        # input a network
        with open(self.filepath) as file:
            print("input start")
            for line in file:
                if line[0] != "#" and len(line) > 1:
                    head, tail = [int(x) for x in line.split()]
                    self.G.add_edge(head, tail)
        file.close()
        "Store the node count and edge count"
        self.node_count = self.G.number_of_nodes()  # 节点数
        self.edge_count = self.G.number_of_edges()  # 边数
        self.deg = self.G.degree()  # G.degree是一个map，key是node valeus是度
        avede = 0.0
        for key in self.G.nodes():
            avede += self.deg[key]
        avede = avede / self.node_count  # 平均度
        print("Nodes number:   " + str(self.node_count))
        print("Edges number:    " + str(self.edge_count))
        print("Average degree:    " + str(avede))

        # collections.defaultdict类的用法，解决dict如果没有对应的key，查询就会error,所以要给个默认值避免，
        # 而defaultdict自动设置了默认值，
        # defaultdict类的初始化函数接受一个类型作为参数，当所访问的键不存在的时候，可以实例化一个值作为默认值；
        self.node_community = defaultdict(int)

        # 每个节点的收益，用来记录是否还有节点的收益发生变化，用于算法的收敛，未来也可以用于记录不平衡节点
        self.utility_nodes = defaultdict(int)
        # Initialize communities of each node
        # 初始化社区，每个节点当作一个社区。

        # zip() 函数是 Python 内置函数之一，它可以将多个序列（列表、元组、字典、集合、字符串以及 range() 区间构成的列表）
        # “压缩”成一个 zip 对象。所谓“压缩”，其实就是将这些序列中对应位置的元素重新组合，生成一个个新的元组。

        # 调用 dict() 函数将 zip() 对象强制转换成字典：
        # 他这句话的意思就是 {(1:1),(2:2),...,(n:n)} 里面一个节点就是一个社区，社区编号就是自己的编号。
        self.node_community = dict(zip(self.G.nodes(), self.G.nodes()))

        # self.utility_list = {node: self.initial_singleton_community(node)[0] for node in self.graphlist.keys()}
        self.utility_nodes = {node: 0 for node in self.G.nodes()}  # 初始每个节点初始收益都设为0

        # 记录是否还有节点的效用值在发生变化
        # 当轮到某个节点进行博弈 而没发生改变的时候会修改为False
        #当这张表全部被修改成False的时候 就是局部纳什均衡
        self.utility_list = {node: True for node in self.G.nodes()}  # 初始都设为True 默认都有改变自己策略的倾向


        #这张表是用来记录节点变化记录的，看看是不是真的来回震荡的就那几个节点。
        self.node_strategy_changetime  = {node: 0 for node in self.G.nodes()}

        # Compute the core groups 从这里开始是构造核心组，你可以看看要不要在这上面继续改造。
        # 其实可以，参考A Four-Stage Algorithm for Community Detection Based on Label Propagation and Game Theory in Social Networks
        # 一开始快速形成一个初始社区有助于加速

        # 那么他构造所谓的核心组，你也可以根据你的亲密度函数来构造你的"核心组"
        # 现在的做法是计算两个节点的平均亲密度。
        # 把节点直接加入平均亲密度最大的邻居的社区。
        # 不会有邻居社区不存在的情况，因为前面初始化的时候设置了一个节点就是一个社区

        # TODO 现在问题是这么粗略地形成社区会影响社区精度
        # 从实验结果来看 初始社区的结构很大一部分就决定了最终社区的结构(LA和newLA的NMI在0.7以上，博弈过程调整了30%)
        # 但博弈特确实对NMI进行了改进，所以现在问题是怎么形成更好的初始社区？

        # 报错了 keyError,因为key是元组(34,17) 34号节点，度是17
        # 这个node要怎么改成self.nodes()
        # for node 本质输出是一个字符串，所以只要取tup[0]就可以了
        for tup in sorted(self.G.degree, key=lambda x: x[1], reverse=True):  # x[1]就是度 按照度降序排列  但这个遍历输出的是元组 不是node
            # for node in sorted(self.G.nodes()):
            # for node in self.G.nodes(): #没降序的话，根本没必要sort，效果相差不大，但少一便sorted
            node = tup[0]
            # The degree of each node
            deg_node = self.deg[node]
            flag = True  # 标记节点是否为核心,True标记是，False标记为不是，初始都标记为True
            maxsimdeg = 0  # 用于记录节点亲密度的最大值,每个节点都是从0开始的
            selected = node
            if deg_node == 1:  # 如果节点的度为1，那么它的社区就是它唯一的那个邻居编号
                self.node_community[node] = self.node_community[list(self.G.neighbors(node))[0]]
            else:  # 其他情况则遍历邻居
                for neig in self.G.neighbors(node):
                    deg_neig = self.deg[neig]  # 邻居的度
                    if flag is True and deg_node <= deg_neig:  # Flag为true且当前节点的度小于等于邻居的度，那么他就不可能是一个核心
                        flag = False  # 标记为false
                        break  # 结束当前节点对邻居的遍历
                '''
                首先每个节点都是初始化为一个社区的
                所以这里没写if flag is True就是默认为True的情况下，就是一个核心节点，不用去加入别人
                '''
                # 判断flag是否为false，如果是False，那么它就要加入一个核心组
                if flag is False:  # 如果遍历完flag为false
                    # 若为false,则按节点的邻居的编号顺序从小到大遍历
                    # 遍历邻居这里sort 不sort有区别吗？反正都是要把所有邻居遍历一遍的
                    # neighbors = sorted(self.G.neighbors(node))  # 按节点编号从小到大排序
                    neighbors = self.G.neighbors(node)  # 按节点编号从小到大排序
                    for neig in neighbors:
                        # 取邻居的度
                        deg_neig = self.deg[neig]
                        # Compute the intimacy coefficient
                        # Compute the node attraction 节点亲密度
                        nodesim_u_v = self.simintimacy(node, neig)[0]
                        nodesim_v_u = self.simintimacy(node, neig)[1]
                        # 目前只是简单的计算平均值 但偏偏效果是最好的 是不是很神奇
                        # 实际上就是AAu_v * ( du + dv) / 2  AA乘以两者度的平均值
                        nodesimdeg = (nodesim_u_v + nodesim_v_u) / 2

                        # 改进一下
                        # 引入以前提到的互动频率的概率
                        # 设置f(i,j) = c/ki+kj-2c 为(i,j)的互动频率
                        # 从公式上就是公共邻居对他们其他度的比率，越高就是互动越频繁
                        # nodesimdeg = self.simintimacy(node, neig)[0]
                        # 改进一下变成公式
                        # Aij * (di+dj) * len(Comm_nei) / (di*dj)
                        # 从结果看反而更差了
                        # comm_neig = set(self.G.neighbors(neig)) & set(self.G.neighbors(node))
                        # nodesimdeg = (nodesim_u_v + nodesim_v_u) * len(comm_neig) / (self.deg[neig] * self.deg[node])

                        # TODO 计算双向亲密度更复杂了以后反而没有更好
                        # #用当前邻居与当前节点的共同邻居数进一步细化
                        # neighbors_now = self.G.neighbors(neig)
                        # #化为集合才能用集合运算符
                        # intersection = set(neighbors_now) & set(neighbors)
                        # len_neigh = len(intersection)
                        # #然后计算双向亲密度
                        # nodesimdeg = (len_neigh / self.deg[neig] + len_neigh / self.deg[node]) * (nodesim_u_v + nodesim_v_u)
                        # 如果和这个邻居节点算出来的节点吸引力，比之前的都要大就更新
                        if nodesimdeg > maxsimdeg:
                            selected = neig  # 要选择的节点
                            maxsimdeg = nodesimdeg  # 更新最大值
                    # 让当前节点加入根据亲密度选中节点selected的社区。
                    self.node_community[node] = self.node_community[selected]

        # 有了核心组以后现在可以计算每个节点的初始收益了
        for node in self.G.nodes():
            # 更新节点的收益为他目前在核心组的收益
            self.utility_nodes[node] = self.utility_function(node, self.node_community[node])
            # self.utility_nodes[node] = self.utility_linear_function(node,self.node_community[node])

    # Simulate the game
    # 在形成核心组的基础上再进行非合作博弈
    #datasetType:看你是要算真实数据集还是人工数据集
    #1 真实 2人工
    def community_detection_game(self, outdirpath, fname,datasetType=1):
        # 用于记录最大度量
        max_NMI = -2.0
        max_ARI = -2.0
        max_Q = -2.0

        maxit = 1  # 设置迭代次数为5 你当然可以设为10
        itern = 0 # 当前迭代回合

        largest_NMI_itern = 0  # 取得最大NMI的回合
        max_node_community = defaultdict(int) #记录下最大社区

        #记录nmi ari 和 Q
        nmilist = []
        arilist = []
        Qlist = []

        # The groundtruth
        LB = []
        # Read the groundtruth communities
        #真实数据集
        if datasetType == 1:
            f_true = open("dataset/" + fname + "_com.dat")
        #人工数据集
        if datasetType == 2:
            # f_true = open("dataset/LFR/LFR1000_u10to80/LFR1000_u" + fname + "/community.dat")
            # f_true = open("dataset/LFR/LFR5000_u10to80/LFR5000_u" + fname + "/community.dat")
            f_true = open("dataset/LFR/LFR10000_u10to80_c100to300/LFR10000_u" + fname + "/community.dat")

        data = f_true.read()
        lines = data.split('\n') #用\n分割开每一行
        for line in lines:
            temp = line.split() #split默认就是一个制表符
            if len(temp) > 1: #如果是1 12 这种形式就表示1号节点12号社区
                self.input_node_community[int(temp[0])] = int(temp[1]) #记录社区

        # LB记录每个节点所属的真实社区
        # eg:
        # LB:[1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 1, 1, 2, 1, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
        LB = [self.input_node_community[k] for k in self.input_node_community.keys()]

        f_true.close()
        # LA记录每个节点所属的算法社区
        # node_community[K]会有分区是因为他已经在上面的store_graphlist函数里计算了核心组。
        # eg:
        # LA:[1, 1, 1, 1, 1, 1, 1, 1, 33, 34, 1, 1, 1, 1, 34, 34, 1, 1, 34, 1, 34, 1, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34]
        # 编号无所谓，metrics会忽略编号，仅比较索引是否在同一社区。
        LA = [self.node_community[k] for k in self.input_node_community.keys()]

        print("LB:" + str(LB))
        print("LA:" + str(LA))

        #所以他实际上把核心组也做了一次对比NMI
        NMI = metrics.normalized_mutual_info_score(LA, LB)

        #经过比较以后，现在的博弈过程(仅加入相邻社区，计算相邻社区的邻居节点的亲密度之和作为效用函数)对小网络的NMI没有太大帮助(0.1以下)
        #对大网络1490 的NMI提升可以到0.1-0.2
        print("初始社区的NMI:" + str(NMI))
        ARI = metrics.adjusted_rand_score(LA, LB)

        #Q的计算要把节点分成一个社区
        #比如parition = [[1,3,4,5,6],[8,54,33,12,44]] 里面一个[]就是一个社区
        #所以问题来了，你要把LA转化成partition才能直接用Q
        partition = self.Lables_to_Partition(LA) #LA是算法分区
        # num = 0
        # for item in partition:
        #     num = num + len(item)
        # print(num)
        Q = modularity(self.G,partition)

        nmilist.append(NMI)
        arilist.append(ARI)
        Qlist.append(Q)

        if (max_NMI < NMI):
            max_NMI = NMI
            largest_NMI_itern = itern
            max_node_community = self.node_community.copy() #获得最佳社区结构到max_node_community 用NMI来评判最佳


        #开始博弈
        print("loop begin:")

        while itern < maxit: #开始博弈，实验maxit次
            itern += 1
            isChange = True
            nums = 0 #记录博弈多少次
            last_node = None #用来记录上一个节点的变量
            while isChange is True: #如果有改变就继续博弈
                '''
                按照以往的经验达到纳什均衡的过程中，可能存在节点策略来回震荡的情况，需要多回合的博弈来稳定
                但达到均衡后社区的精度并没有发生明显的提升，因此没有必要完全达到纳什均衡再停止
                可以设置一个平衡节点，当平衡节点数量达到总节点的α倍就结束。
                '''
                node = random.choice(list(self.G.nodes())) #随机选择博弈节点
                if last_node == node: #如果和上回合选的节点一样就没必要博弈了，重新选
                    continue
                else:
                    last_node = node #如果不一样就赋给last_node，继续记录下上一个节点是谁
                #用于纳什均衡的参数，当nochangeNum == self.node_count的时候 就是均衡了
                nochange_num = 0
                # 尝试加入让效用函数最大的邻居社区
                join = self.join_neigh_community(node)
                # 尝试离开当前社区 现在是单社区，我们不允许节点没有社区，所以这个leave的效用只能是0，所以就不浪费时间去算了
                # leave = self.leave_community(node)
                leave = 0
                # 开始比较三个动作之后效用函数的大小
                if join[1] > leave:
                    self.node_community[node] = join[0]  # 加入这个邻居社区  #TODO 原来会越来越好，原来玄机在这里，后面的博弈都是在前面的基础上，前面已经让这些节点加入了大概率会更好的社区 所以后面的博弈效果都很好
                    self.utility_nodes[node] = join[1]
                    #变化一次就+1
                    self.node_strategy_changetime[node] = self.node_strategy_changetime[node] + 1
                    for key in self.utility_list.keys(): #只要有一个节点发生改变，就要全部重新设为True进行博弈
                        self.utility_list[key] = True
                    # self.utility_list[node] = True  # 记录为True，节点的社区变化了
                #TODO 单社区并没有离开操作，只有切换操作。
                elif leave > join[1]:  # 这个条件单社区其实是不会发生的
                    print("我真的不会发生")
                    self.node_community[node] = self.node_count + 1
                    self.utility_nodes[node] = leave
                    for key in self.utility_list.keys(): #只要有一个节点发生改变，就要全部重新设为True进行博弈
                        self.utility_list[key] = True
                # 第三个if其实就是等于，那什么都不做 do nothing
                else:
                    self.utility_list[node] = False  # False，啥也没干
                #问题在这里，把所有节点都访问一次以后就可以结束了吗？？
                #应该是所有节点访问一圈都没有人选择改变策略 才是结束吧
                #nochange_num = 0 #没改变的数量，每轮都要重置为0，所以写在for外面，while里面
                '''
                把下面这段纳什均衡的注释了 效果反而更好
                因为这个非合作纳什均衡有大问题，你只是简单判断所有节点是不是False就结束了
                因为你初始的utility_list全都是False。
                如果你随机选择的节点刚好没有变化，那整个list就全都是False，
                导致就博弈了一两个回合就直接纳什均衡了，那肯定只能得到错误的结果
                那你改成初始全为True不就好了吗
                '''
                # TODO 看上面 这显然错误。所以还是要修改啊
                for node in self.G.nodes():
                    if self.utility_list[node] == False:
                        nochange_num = nochange_num + 1
                        if nochange_num == self.node_count: #如果全是Fasle，节点的策略都没再改变，那就是纳什均衡了。
                            isChange = False
                            print("我是局部纳什均衡停下来的")
                #没有博弈次数限制也可以停下来，但是过程比较随机，可能会等待比较久。而且精度反而更低
                #人为设置停止似乎也是个办法。
                #上面的纳什均衡绝对是存在问题的，所以暴力点，博弈5N次停下来，至少效果不会差太多
                nums = nums + 1 #博弈的次数
                # 其实每次都博弈2次，然后后面再根据前面的基础继续博弈，试了一下基本上博弈数在12倍节点数就可以达到博弈最优
                # 一万个节点 大概要30倍才能跑到均衡，修改maxit为1次
                # 傻逼博弈，这样跑要贼TM久。
                if (nums == (5 * self.node_count)):
                    isChange = False  # 所有节点都不改变了才是False
                    print("我是博弈次数到节点的2倍就停下来的")

            print(self.node_strategy_changetime)
            total_change = 0

            for key,value in self.node_strategy_changetime.items():
                if value > 0:
                    total_change = value + total_change



            newLA = [self.node_community[k] for k in self.input_node_community.keys()]
            # print("非合作博弈后newLA:" + str(newLA))
            NMI_LA_newLA = metrics.normalized_mutual_info_score(newLA,LA) #比较LA 和 newLA 有多少相似（改变）
            print("非合作博弈后newLA对比LA的相似度(NMI)是:" + str(NMI_LA_newLA) + ",非合作博弈后产生的不同为" + str(1 - NMI_LA_newLA)) #用来比较博弈到底产生了多大作用

            NMI = metrics.normalized_mutual_info_score(newLA, LB)
            ARI = metrics.adjusted_rand_score(newLA, LB)

            partition = self.Lables_to_Partition(newLA)  # LA是算法分区
            Q = modularity(self.G,partition)

            nmilist.append(NMI)
            arilist.append(ARI)
            Qlist.append(Q)

            if (max_NMI < NMI):
                #更新为迭代回合中最大的那个指标
                max_NMI = NMI
                largest_NMI_itern = itern
                max_node_community = self.node_community.copy() #记录下这maxit次迭代的最佳NMI分区
            if (max_ARI < ARI):
                # 更新为迭代回合中最大的那个指标
                max_ARI = ARI
            if(max_Q < Q):
                # 更新为迭代回合中最大的那个指标
                max_Q = Q

            print("max_NMI:" + str(max_NMI))
            print("\n")

        print("uncooperate done")


        self.node_community = max_node_community.copy()

        self.graph_result = defaultdict(list)

        for item in self.node_community.keys():
            node_comm = int(self.node_community[item])
            #一个[node_comm]对于一个list就是一个社区
            self.graph_result[node_comm].append(item)

        if datasetType == 1:
            f = open(outdirpath + "/" + fname + ".txt", "w+")
            #分区文件写到fname_partition.txt里面
            f1 = open(outdirpath + "/" + fname + "_partition.txt","w+")
        if datasetType == 2:
            # f = open(outdirpath + "/LFR_LFR1000/u" + fname + "_result.txt", "w+")
            # f = open(outdirpath + "/LFR_LFR5000/u" + fname + "_result.txt", "w+")
            f = open(outdirpath + "/LFR_LFR10000/u" + fname + "_result.txt", "w+")
            # 分区文件写到fname_partition.txt里面
            # f1 = open(outdirpath + "/LFR_LFR1000/u" + fname + "_result_partition.txt", "w+")
            # f1 = open(outdirpath + "/LFR_LFR5000/u" + fname + "_result_partition.txt", "w+")
            f1 = open(outdirpath + "/LFR_LFR10000/u" + fname + "_result_partition.txt", "w+")
        # print(self.graph_result)
        for keys,values in self.graph_result.items():
            f1.write(str(values).strip('[').strip(']'))
            f1.write('\n')
        f.write("community number:  \n")
        f.write(str(len(self.graph_result.keys())))
        f.write("\n\n\n")
        f.write("loop number:  \n")
        f.write(str(itern))
        f.write("\n\n\n")
        f.write("The best partition in loop:     \n")
        f.write("itern = " + str(largest_NMI_itern))
        f.write("\n\n\n")
        f.write("The highest NMI value: \n")
        f.write(str(max_NMI))
        f.write("\n\n\n")
        f.write("The highest ARI value: \n")
        f.write(str(max_ARI))
        f.write("\n\n\n")
        f.write("The highest Q value: \n")
        f.write(str(max_Q))
        f.write("\n\n\n")
        f.write("All NMI values: \n")
        f.write(str(nmilist))
        f.write("\n\n\n")
        f.write("All ARI values:     \n")
        f.write(str(arilist))
        f.write("\n\n\n")
        f.write("All Q values:     \n")
        f.write(str(Qlist))
        f.close()


        '''
        #从下面开始加入合作博弈部分
        '''
        print("--------------------------------------------------------------------------------------")
        #把之前非合作的度量清理一下
        nmilist.clear()
        arilist.clear()
        Qlist.clear()
        '''
        #社区的停止标记有点麻烦不能像节点一样所有节点都不在变化了就可以停止了
        '''
        #用于停止的标记
        # self.alliance_change_dict = {key: False for key in self.graph_result.keys()}  # 初始都设为False 即没有变化
        # 非合作后的最佳是社区保存在graph_result里面
        #keys是社区编号，values是对应的社区结构
        original = {}
        for keys, values in self.graph_result.items():
            original[keys] = values
        #副本给original以后，就可以清空用作合作的结果了
        #因为合作博弈如果NMI变大，要把当前最好的社区结构COPY给graph_result
        self.graph_result.clear()
        #开始尝试合作
        cooperItern = 0 #合作博弈的迭代次数
        print("cooperate begin:")
        while cooperItern < maxit:  # 开始博弈，实验maxit次
            cooperItern = cooperItern + 1 #记录循环次数
            partition.clear() #每个合作博弈开始清空partition 防止partition生成的新的社区编号造成keyError
            #不能直接等号，不然除了第一次，每次都会使用修改后的partition
            #要copy一下
            partition = original.copy() #每个合作博弈大回合的开始要还原成非合作博弈的分区结果
            isChange = True
            best = -1 #最佳合并社区的编号
            last_community = None  # 用来记录上一个社区的变量
            merging_number = 0 #真正合并的次数
            chose_community = -1 #记录当前社区
            merging_community = -1 #记录被合并的社区号
            compare_number = 0  # 比较次数初始设为0，因为没有发生合并的话，compare_number不用重置0，所以放while外面
            #开始合作博弈
            while isChange is True:  # 如果有改变就继续博弈
                #这个收益函数肯定有问题，最后大家都到一起了。
                #因为partition每次博弈都可能会更新，就导致每回合都要更新all_coaliation_utility
                '''
                怎么解决合并成一个社区的问题，修改合作博弈的目标函数
                '''
                if len(partition.keys()) == 1:
                    break
                all_coaliation_utility = self.coaliation_utility(partition)
                community = random.choice(list(partition.keys()))  # 随机选择博弈社区
                if last_community == community:  # 如果和上回合选的节点一样就没必要博弈了，重新选
                    continue
                else:
                    last_community = community  # 如果不一样就赋给last_community，继续记录下上一个社区是谁
                #每次比较完partition可能都会变，所以要把最大比较次数放里面
                max_compare_number = math.comb(len(partition.keys()), 2)  # 最大比较次数Cn2
                # 找最佳合并社区
                #字典迭代的时候不能改变字典的大小
                #只能记录下要删除的Key 迭代完以后更改字典大小。
                max_deta_x = 0 #每次博弈都要把max_deta_x 换为0 -'inf'表示无穷小
                flag = False # 用于记录是否真的能改变的标记
                for key in partition.keys():
                    # print("partition.keys()长度的变化情况"+str(len(partition.keys())) + "具体是:" + str(partition.keys()) )
                    # 这样比较的话,compare_number其实最大是 n*(n-1)，就是每个社区都和其他社区进行比较。而不是C(n,2)选过的社区就不再选了。
                    # 但问题就是这个，合作博弈过程中社区数量会减少，相同的社区号，但是社区内容可能已经不一样了，
                    # 这就导致每次博弈一定要让当前选择社区和所有其他社区都进行一次尝试合并才行。
                    # 换句话说就是博弈次数一定是 ∑n*(n-1) (n是每回合的社区数,至于要迭代多少回合，那得一直到没有两个社区能够合并为止，这个条件太慢了)
                    # 现在的停止条件是当前回合的n*(n-1)如果大于等于C(n,2)，就提前停止
                    # 但是其实这个条件是废话，n*(n-1) 一定大于等于 C(n,2)= n*(n-1)/2
                    # 这个条件就相当于如果这个回合的迭代次数达到最大比较次数的一半的时候都没有发生合并的话，就提前停止合作博弈。
                    # 所以加了个保险当发生合并了以后compare_number就要重新置为0，继续重复这个过程。

                    # 但是问题就出现了 当非合作博弈形成的社区数非常多的时候(社区数接近节点数)
                    # 合作博弈的时间复杂度是 O(T* N^2 * N^2) 可能会达到O(Tn^4)
                    # 第一个n^2是比较次数，第二个n^2是计算尝试合并社区的效用
                    # 这实在是太慢了，你要尝试剪枝啊。

                    if key != community: #如果当前选中的社区不一样
                        compare_number = compare_number + 1 #比较1次就加1
                        #取并集
                        union = list(set(partition[key]) | set(partition[community]))
                        # 如果两个社区的效用都变大才会合并
                        # 暂时修改partition[key]联盟里的节点社区编号为community
                        for node in partition[key]:
                            self.node_community[node] = community
                        #然后计算效用值
                        union_utility = self.coaliation_utility({community: union})
                        #因为只是为了计算模拟的效用值，并不一定会真的合并，所以算完记得改回来
                        for node in partition[key]:
                            self.node_community[node] = key
                        # 如果合作的效用，比原来各自的效用大，这个条件太苛刻，在非博弈合作以后比较难以实现
                        # 这个条件只有polblogs里面生效，提升了0.01 其他数据集都没什么效果
                        # if union_utility[community] > all_coaliation_utility[key] and union_utility[community] > all_coaliation_utility[community]:
                        # 修改条件为，如果合作后，两个社区的效用改变之和是提升的，那就合并
                        if (union_utility[community] - all_coaliation_utility[key]) + (union_utility[community] - all_coaliation_utility[community]) > 0:
                            #不能一变大就修改，要找那个合并后收益最大的社区
                            #所有只能暂时先记录下变化值
                            deta_x = union_utility[community] - all_coaliation_utility[key] + union_utility[community] - all_coaliation_utility[community]
                            if deta_x > max_deta_x:
                               max_deta_x = deta_x
                               best = key #记录最佳合并社区
                               chose_community = community
                               merging_community = key
                               flag = True #是真的能合并的社区，而不是上一次记录的best。因为上次的best已经被合并删除了。

                #找到最佳合并社区以后开始尝试合并
                # 如果best发生了改变，也就是发生了合并才执行下面的更新
                # best= -1的话 说明就没有发生过更好的选项
                if best != -1 and flag == True:
                    merging_number = merging_number + 1
                    # 1.更新最佳合并社区best中的节点社区号为community
                    for node in partition[best]:
                        self.node_community[node] = community
                    #2.更新union
                    union = list(set(partition[best]) | set(partition[community]))
                    #3.partition要弹出被合并的社区，因为原来的社区被合并也就不存在了
                    partition.pop(best)
                    #4.partition要更新新社区
                    partition[community] = union
                    #最后记得发生了合并，把compare重置为0，继续博弈，防止compare_number > max 就结束了。
                    compare_number = 0
                #TODO 最后的问题是什么时候才能停止社区合并 现在while还没有停止条件
                #暂时把博弈回合数设置成Cn2，也就是随机选择两个社区合并的组合数，如果超过这个博弈次数就中止
                #这个条件还得改一改，社区数特别多的时候，例如人工网络u特别大的时候，算法会把1000个节点的网络分成的500个左右小社区，这样组合数就会特别大，
                #那要来回跑几十万几百万个回合，显然是不科学的
                if compare_number >= max_compare_number:
                    isChange = False #停止比较，本次合作博弈结束，开始下一次

            print("真正合并的次数" + str(merging_number))
            cooperateLA = [self.node_community[k] for k in self.input_node_community.keys()]
            print("合作博弈后cooperLA:" + str(cooperateLA))
            NMI_LA_newLA = metrics.normalized_mutual_info_score(cooperateLA, newLA)  # 比较cooperateLA 和 newLA 有多少相似（改变）
            print("合作博弈后cooperLA对比uncooperLA的相似度(NMI)是:" + str(NMI_LA_newLA) + ",合作博弈后产生的不同为" + str(
                1 - NMI_LA_newLA))  # 用来比较博弈到底产生了多大作用

            NMI = metrics.normalized_mutual_info_score(cooperateLA, LB)
            print("本次选择合并的社区为:" + str(chose_community) + "," + str(merging_community))
            print("本次合作NMI为:" + str(NMI))
            ARI = metrics.adjusted_rand_score(cooperateLA, LB)

            newPartition = self.Lables_to_Partition(cooperateLA)  # cooperateLA是算法分区
            Q = modularity(self.G, newPartition)

            nmilist.append(NMI)
            arilist.append(ARI)
            Qlist.append(Q)

            if (max_NMI < NMI):
                # 更新为迭代回合中最大的那个指标
                print("合作博弈让NMI增大了")
                max_NMI = NMI
                largest_NMI_itern = cooperItern
                max_node_community = self.node_community.copy()  # 记录下这maxit次迭代的最佳NMI分区
            if (max_ARI < ARI):
                # 更新为迭代回合中最大的那个指标
                print("合作博弈让ARI增大了")
                max_ARI = ARI
            if (max_Q < Q):
                # 更新为迭代回合中最大的那个指标
                print("合作博弈让Q增大了")
                max_Q = Q
            print("max_NMI:" + str(max_NMI))
            print("\n")

        print("cooperate done")

        #合作博弈结束后把NMI最佳的社区赋值结果
        #max_node_community记录的是最大NMI的社区结构
        self.node_community = max_node_community.copy()

        #更新为最终结果
        for item in self.node_community.keys():
            node_comm = int(self.node_community[item])
            # 一个[node_comm]对于一个list就是一个社区
            self.graph_result[node_comm].append(item)

        # print(self.graph_result)
        #从这里开始loop循环结束
        '''
        #开始写文件
        '''
        if datasetType == 1:
            f = open(outdirpath + "/" + fname + "_cooper_result.txt", "w")
            # 分区文件写到fname_partition.txt里面
            f1 = open(outdirpath + "/" + fname + "_cooper_partition.txt", "w")
        if datasetType == 2:
            # f = open(outdirpath + "/LFR_LFR1000/u" + fname + "_cooper_result.txt", "w")
            # f = open(outdirpath + "/LFR_LFR5000/u" + fname + "_cooper_result.txt", "w")
            f = open(outdirpath + "/LFR_LFR10000/u" + fname + "_cooper_result.txt", "w")
            # 分区文件写到fname_partition.txt里面
            # f1 = open(outdirpath + "/LFR_LFR1000/u" + fname + "_result_cooper_partition.txt", "w")
            # f1 = open(outdirpath + "/LFR_LFR5000/u" + fname + "_result_cooper_partition.txt", "w")
            f1 = open(outdirpath + "/LFR_LFR10000/u" + fname + "_result_cooper_partition.txt", "w")
            # print(self.graph_result)
        for keys, values in self.graph_result.items():
            f1.write(str(values).strip('[').strip(']'))
            f1.write('\n')
        f.write("Cooperative Game \n\n\n")
        f.write("final community number:  \n")
        f.write(str(len(self.graph_result.keys())))
        f.write("\n\n\n")
        f.write("The best partition in cooperate loop:     \n")
        f.write("itern = " + str(largest_NMI_itern))
        f.write("\n\n\n")
        f.write("The highest NMI value: \n")
        f.write(str(max_NMI))
        f.write("\n\n\n")
        f.write("The highest ARI value: \n")
        f.write(str(max_ARI))
        f.write("\n\n\n")
        f.write("The highest Q value: \n")
        f.write(str(max_Q))
        f.write("\n\n\n")
        f.write("All NMI values: \n")
        f.write(str(nmilist))
        f.write("\n\n\n")
        f.write("All ARI values:     \n")
        f.write(str(arilist))
        f.write("\n\n\n")
        f.write("All Q values:     \n")
        f.write(str(Qlist))
        f.close()

    '''
    三个动作，离开当前社区，切换到邻居社区，留在当前社区
    返回值是进行动作后的收益
    '''

    # 离开当前社区
    def leave_community(self, node):
        # 获取当前所有社区的编号
        community_ids = set(self.node_community.values())
        # 随机生成一个不在社区编号集合中的新编号
        new_community_id = max(community_ids) + 1 if community_ids else 0
        #如果新生成的id在社区编号中 就给他加1
        while new_community_id in community_ids:
            new_community_id += 1
        # 计算离开当前社区后的收益
        utility_leave = self.utility_function(node, new_community_id)
        return utility_leave

    # 离开当前社区，加入邻居社区，加入那个令他效用最大的社区
    def join_neigh_community(self, node):
        best_comm = -1  # 记录要加入的社区编号
        max_utility = 0.0  # 记录最大的效用值
        neiglist = self.G.neighbors(node)
        communities_neigh = set()
        for neig in neiglist:
            C = self.node_community[neig]
            communities_neigh.add(C)  # 将邻居社区添加到邻居社区集合中，用无序来保证随机访问。

        node_community = self.node_community[node]  # 取出博弈过程中变化的当前node社区
        utility_now = self.utility_nodes[node]  # 博弈过程中节点的收益

        # 遍历相邻的社区，并尝试加入，最终会加入使得效用最大的那个社区
        for c in communities_neigh:
            if c == node_community:  # 如果c和节点的当前社区一致就没必要算了(本来就在一起，还加入什么),算下一个相邻的c
                continue
            # 如果和当前社区不一样
            utility_neig = self.utility_function(node, c)  # 计算节点node加入社区c能获得的收益
            if utility_neig > utility_now and utility_neig > max_utility:  # 如果变得最大，则考虑加入新的社区，
                max_utility = utility_neig
                best_comm = c
        # 返回[c,max_utility] 要加入的社区和能得到的最大收益max_utility
        return [best_comm, max_utility]

    # 其实下面应该还有个do_nothing 但其实就是加入和离开动过效用等于的情况就什么都不用做
    def do_nothing(self):
        pass

    #社区的总收益
    # 对社区内的每个节点我们设置他的特征函数是  内在度/自己的整度 (内再度 节点u与社区内其他节点v的连接边数)
    # 社区的特征函数就是社区内节点的特征函数之和
    #只是简单的内再度/自己度之和作为特征函数根本没作用 那样所有节点都在一个社区就能获得最大的效用max=N

    #最常用的是 Q(S)= 2e(S)/|S| - (|S|/2|E|)^2  e(S)是S所有节点内再度之和，|S|是所有节点度之和 |E|是总边数
    #TODO 更新成上面那个还是一点效果没有，合作博弈要怎么加进来？？
    def coaliation_utility(self,partition):
        coaliation_utility = {}
        # for key in partition.keys():
        #     s_degree_sum = self.s_degree_sum(key,partition) #当前社区的总度，把partition也传进去，避免遍历整个网络。
        #     e_S = self.s_in_link_number(key,partition) #计算社区s内的边数量
        #     # s_per = 0.0 #内在度
        #     # for node in partition[key]:
        #     #     # 计算每个社区节点的内在度之和
        #     #     s_per = s_per + self.per(node,self.node_community[node])
        #     # Q(S)= e(S)/D(S) - (D(S)/2|E|)^2 这个就是模块度公式把前面内聚性的分母从E改成了D(S)，前面是内聚性程度，后面是惩罚项，合并成一个社区时惩罚最大，但其实4E^2是个固定常数，根本没什么计算的价值。
        #     # 其实这个Q(S)就是仿照模块度。很无语，所以你的合作博弈函数用这个，那目的就变成了提高模块度。
        #     # s_utility = (s_per / s_degree_sum) - (s_degree_sum / (2 * self.edge_count))**2
        #     s_utility = (e_S / s_degree_sum) - (s_degree_sum / (2 * self.edge_count))**2
        #     # 模块度原公式 e(S)/|E| - (D(S)/2|E|)^2
        #     # s_utility = (e_S / self.edge_count) - (s_degree_sum / (2 * self.edge_count))**2
        #     coaliation_utility[key] = s_utility


        # v(S) = 0 |S| = 1
        #      =  ∑ per(i,S)/deg(i) |S|>=2 deg(i)!=0
        # 这个合作是有合作，但是大多时候是在瞎合作，把原来应该分开的社区给合到了一起
        # for key in partition.keys():
        #     # 如果是单个社区的集合,则没有意义，设置为0
        #     if len(partition[key]) == 1:
        #         coaliation_utility[key] = 0
        #     else:
        #         # 其他情况就遍历合并社区中的节点，计算每个节点对联盟Sj的内在度减去它外在度的差值，然后除以自己的度，实际上这个公式等于 2a/k - 1 a表示节点i的内在度，k表示总度
        #         sum = 0.0
        #         for node in partition[key]:
        #             #2a/k - 1
        #             sum = sum + ( 2 * self.per(node, self.node_community[node]) / self.deg[node] - 1)
        #         coaliation_utility[key] = sum

        '''
        或者按照2014_一种基于合作博弈的社区检测算法
        Pout>=Pin的时候说明这个社区不合理，让这个社区与Pout最大的社区进行合并
        根据这个思路，我们让收益函数为Pin - Pout，如果两者都能更大，则进行合并。
        但问题在于这样简单的设计会让所有社区都合并在一起，最好Pin就是D（G）,Pout=0
        所以还应该加上一个合并的惩罚项，避免过度合并
        v(S) = (Pin - Pout)/Pin - (Pin/|E|)^2
        这样当所有节点合并在一起的时候 v(S)的值就是 1 - 1 = 0
        
        现在问题是用这个效用函数就需要把合作的条件：合作后两者的效用都要不少于合作前的效用
        但问题就在于非合作博弈以后形成的社区都有较强的内聚性，这些社区不愿意在没有提升，甚至是会使自身效用降低的情况下去合作帮助别的社区提升效用值
        
        如果把合作的条件削弱，改成：合作后两者效用值的变化量大于0，则doplhin网络可以从0.6759提升到0.8888
        '''
        for key in partition.keys():
            in_nums = self.s_in_link_number(key,partition)
            out_nums = self.s_out_link_number(key,partition)
            diff = in_nums - out_nums
            #有的社区只有单个节点，那么他们的内在边数量就是0
            #对于0应该另外设置一套v_S，在这里只是简单的用-(diff/E)^2
            if in_nums == 0:
                v_S = -(diff / self.edge_count) ** 2
            else:
                v_S = (diff / in_nums) -  ( in_nums / self.edge_count) ** 2
            coaliation_utility[key] = v_S
        return coaliation_utility

    # The internal degree of node v in a community
    # 计算节点v在单独社区c中的内在度in_v
    # 也就是节点v与社区C中其他节点的边数的和
    # 社区为单个节点的内在度为0
    def per(self, v,c):
        neiglist1 = self.G.neighbors(v)  #v节点的邻居列表
        in_v = 0
        self.nodecount_comm = defaultdict(int)
        for neig in neiglist1:
            if self.node_community[neig] == c: #如果邻居社区也包含c
                in_v += 1 #v对社区c的内在度+1
            else: #否则把这个社区对应的key+1
                self.nodecount_comm[self.node_community[neig]] += 1
        per = in_v
        return per
    '''
    算联盟s的总度数
    s是社区编号
    partition记录了当前社区结构
    '''
    def s_degree_sum(self, s,partition):
        sum = 0
        for node in partition[s]:
            sum = sum + self.deg[node]
        return sum

    '''
    计算社区s内的连边数量，不是内在度之和！
    
    这里又要小心处理一下，不知道为什么polblogs数据集把1259分成了自己一个社区，可能是1260是一个环，内聚性强和别人玩不到一起
    那么partition只有一个节点是一个社区的话，就得特殊处理了
    '''
    def s_in_link_number(self, s, partition):
        #如果是特殊情况，社区只有，一个点，那么这个社区s内的连边数量为0
        if(len(partition[s]) == 1):
            return 0
        #其他多个节点的社区
        nodes = partition[s]  # get the nodes in community s
        num_links = 0  # initialize the number of links to zero
        for u in nodes: # 遍历社区s
            rest = set(nodes)  # make a copy of the set
            rest.remove(u)  # remove u from the set
            #是不是要判定一下rest不为空才继续
            for v in rest:
                if self.G.has_edge(u,v):  # 不能用is not None，因为直接用edge(u,v)来判断是否有边，会返回True/False 都不是None 那么无论是否存在边都会+1
                    num_links += 1  # increment the number of links
            #遍历完u节点后，nodes去掉u，直接指向新地址即可
            nodes = rest  # nodes指向新的地址
        return num_links

    '''
    社区外边数Pout
    实际上Pout = D(S) - ∑ per(i,S)=总度 - 内在度之和
    '''
    def s_out_link_number(self, s, partition):
        D_S = self.s_degree_sum(s,partition)
        per_S = 0
        for node in partition[s]:
            per_S = per_S + self.per(node,s)
        out_link_nums = D_S - per_S
        return out_link_nums

    '''
    用于从社区标签到分区的函数，
    eg: 
    LA=[1, 1, 1, 1, 1, 1, 1, 1, 33, 10, 1, 1, 1, 1, 34, 34, 1, 1, 34, 1, 34, 1, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34]
    化成
    partition = [[1,2,3,4,5,6,7,...],[22],[12,13,14,15,...]]一个[]就是一个社区，里面是具体的社区成员编号（从1开始)
    '''
    def Lables_to_Partition(self,LA):
        partition = []
        temp = []
        #copy_LA = LA.copy() #复制一份LA
        #然后用set去重,然后用list保证顺序 这样community_number里就只剩下社区编号[1,33,10,34]了
        community_number = list(set(LA))

        #TODO 这里先遍历社区有很大问题啊 先遍历社区再遍历节点 那么算法复杂度是O(mn) n是节点数,m是社区数
        for community in community_number:
            for index in range(0,len(LA)): #左闭右开
                if LA[index] == community:
                    temp.append(index + 1) #把节点序列添加到temp里 python list的添加用append方法 +1是为了让节点从1开始
            partition.append(temp)
            temp = [] #清空temp
        #print(partition)
        return partition #最后就得到partition了