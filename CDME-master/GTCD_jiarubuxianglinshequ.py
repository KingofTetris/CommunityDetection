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

    #造图
    def store_graphlist(self, fname):
        # graph
        self.G = nx.Graph()        
        self.input_node_community = defaultdict(int)
        #input a network
        with open(self.filepath) as file:
            print(" input start")
            for line in file:
                if line[0] != "#" and len(line) > 1:
                    head, tail = [int(x) for x in line.split()]
                    self.G.add_edge(head, tail)
        file.close()
        "Store the node count and edge count"
        self.node_count = self.G.number_of_nodes() #节点数
        self.edge_count = self.G.number_of_edges() #边数
        self.deg = self.G.degree()    #G.degree是一个map，key是node valeus是度
        avede = 0.0
        for key in self.G.nodes():
            avede += self.deg[key]
        avede = avede/self.node_count #平均度
        print ("Nodes number:   " + str(self.node_count))
        print ("Edges number:    " + str(self.edge_count))
        print ("Average degree:    " + str(avede))


        #collections.defaultdict类的用法，解决dict如果没有对应的key，查询就会error,所以要给个默认值避免，
        # 而defaultdict自动设置了默认值，
        # defaultdict类的初始化函数接受一个类型作为参数，当所访问的键不存在的时候，可以实例化一个值作为默认值；
        self.node_community = defaultdict(int)

        #每个节点的收益，用来记录是否还有节点的收益发生变化，用于算法的收敛，未来也可以用于记录不平衡节点
        self.utility_nodes = defaultdict(int)
        # Initialize communities of each node
        # 初始化社区，每个节点当作一个社区。

        #zip() 函数是 Python 内置函数之一，它可以将多个序列（列表、元组、字典、集合、字符串以及 range() 区间构成的列表）
        # “压缩”成一个 zip 对象。所谓“压缩”，其实就是将这些序列中对应位置的元素重新组合，生成一个个新的元组。

        # 调用 dict() 函数将 zip() 对象强制转换成字典：
        # 他这句话的意思就是 {(1:1),(2:2),...,(n:n)} 里面一个节点就是一个社区，社区编号就是自己的编号。
        self.node_community = dict(zip(self.G.nodes(), self.G.nodes()))

        # self.utility_list = {node: self.initial_singleton_community(node)[0] for node in self.graphlist.keys()}
        self.utility_nodes = {node : 0 for node in self.G.nodes()} #初始每个节点初始收益都设为0

        #记录是否还有节点的效用值在发生变化
        self.utility_list = {node : False for node in self.G.nodes()} #初始都设为False 即没有变化
       
        #Compute the core groups 从这里开始是构造核心组，你可以看看要不要在这上面继续改造。
        # 其实可以，参考A Four-Stage Algorithm for Community Detection Based on Label Propagation and Game Theory in Social Networks
        # 一开始快速形成一个初始社区有助于加速

        #那么他构造所谓的核心组，你也可以根据你的亲密度函数来构造你的"核心组"
        # 现在的做法是计算两个节点的平均亲密度。
        # 把节点直接加入平均亲密度最大的邻居的社区。
        # 不会有邻居社区不存在的情况，因为前面初始化的时候设置了一个节点就是一个社区

        # TODO 现在问题是这么粗略地形成社区会影响社区精度
        # 从实验结果来看 初始社区的结构很大一部分就决定了最终社区的结构(LA和newLA的NMI在0.7以上，博弈过程调整了30%)
        # 但博弈特确实对NMI进行了改进，所以现在问题是怎么形成更好的初始社区？


        #报错了 keyError,因为key是元组(34,17) 34号节点，度是17
        #这个node要怎么改成self.nodes()
        #for node 本质输出是一个字符串，所以只要取tup[0]就可以了
        for tup in sorted(self.G.degree, key=lambda x: x[1], reverse=True): #x[1]就是度 按照度降序排列  但这个遍历输出的是元组 不是node
        # for node in sorted(self.G.nodes()):
        # for node in self.G.nodes(): #没降序的话，根本没必要sort，效果相差不大，但少一便sorted
            node = tup[0]
            #The degree of each node
            deg_node = self.deg[node]
            flag = True  #标记节点是否为核心,True标记是，False标记为不是，初始都标记为True
            maxsimdeg = 0   #用于记录节点亲密度的最大值,每个节点都是从0开始的
            selected = node            
            if deg_node == 1: #如果节点的度为1，那么它的社区就是它唯一的那个邻居编号
                self.node_community[node] = self.node_community[list(self.G.neighbors(node))[0]]
            else:               #其他情况则遍历邻居
                for neig in self.G.neighbors(node):                   
                    deg_neig = self.deg[neig]       #邻居的度
                    if flag is True and deg_node <= deg_neig: #Flag为true且当前节点的度小于等于邻居的度，那么他就不可能是一个核心
                        flag = False #标记为false
                        break # 结束当前节点对邻居的遍历

                #判断flag是否为false，如果是False，那么它就要加入一个核心组
                if flag is False: #如果遍历完flag为false
                    # 若为false,则按节点的邻居的编号顺序从小到大遍历
                    # 遍历邻居这里sort 不sort有区别吗？反正都是要把所有邻居遍历一遍的
                    # neighbors = sorted(self.G.neighbors(node))  # 按节点编号从小到大排序

                    neighbors = self.G.neighbors(node)  # 按节点编号从小到大排序
                    for neig in neighbors:
                        #取邻居的度
                        deg_neig = self.deg[neig]
                        # Compute the intimacy coefficient
                        # Compute the node attraction 节点亲密度
                        nodesim_u_v = self.simintimacy(node, neig)[0]
                        nodesim_v_u = self.simintimacy(node, neig)[1]
                        #目前只是简单的计算平均值
                        #实际上就是AAu_v * ( du + dv) / 2  AA乘以两者度的平均值
                        nodesimdeg = (nodesim_u_v + nodesim_v_u) / 2

                        #TODO 计算双向亲密度更复杂了以后反而没有更好
                        # #用当前与当前邻居与当前节点的共同邻居数进一步细化
                        # neighbors_now = self.G.neighbors(neig)
                        # #化为集合才能用集合运算符
                        # intersection = set(neighbors_now) & set(neighbors)
                        # len_neigh = len(intersection)
                        # #然后计算双向亲密度
                        # nodesimdeg = (len_neigh / self.deg[neig] + len_neigh / self.deg[node]) * (nodesim_u_v + nodesim_v_u)

                        #如果和这个邻居节点算出来的节点吸引力，比之前的都要大就更新
                        if nodesimdeg > maxsimdeg:
                            selected = neig #要选择的节点
                            maxsimdeg = nodesimdeg #更新最大值

                        #让当前节点加入根据亲密度选中节点selected的社区。
                        self.node_community[node] = self.node_community[selected]

        #有了核心组以后现在可以计算每个节点的初始收益了
        for node in self.G.nodes():
            #更新节点的收益为他目前在核心组的收益
            self.utility_nodes[node] = self.utility_function(node,self.node_community[node])
            # self.utility_nodes[node] = self.utility_linear_function(node,self.node_community[node])


    #Compute the jaccard similarity coefficient of two node
    def simjkd(self, u, v):        
        set_v = set(self.G.neighbors(v))
        set_v.add(v)
        set_u = set(self.G.neighbors(u))
        set_u.add(u)
        jac = len(set_v & set_u) * 1.0 / len(set_v | set_u)    #集合相与取交集，相或取并集。
        return jac

    # Compute the intimacy coefficient of two node
    #  u->v u对v的吸引力 因为参考现实中两个人的亲密度其实是不同的
    # 所以我们设置两个方向的吸引力，目前的区别仅仅是采用了各自的度

    #原始AA版本
    def simintimacy(self,u,v):
        set_v = set(self.G.neighbors(v))
        set_u = set(self.G.neighbors(u))
        neighbors = set_v & set_u # u和v的公共邻居


        # 但是AA指数对于直接连边的节点对亲密度居然是0，这个时候我们要特殊处理一下节点对有直接连边 但是没有公共邻居的情况
        # if len(neighbors) == 0 and self.G.edges(u,v) is not None:
        #     #两者虽然没有公共邻居，但是直接连边的关系让亲密度也不会很低
        #     #TODO 我们暂时让这个节点对的亲密度设为这条边的权重为两个节点的度数之和的一半
        #     # 实验后看结果，这样处理了也没有太大差别。
        #     avg = (self.deg[u] + self.deg[v]) / 2
        #     return[avg,avg]

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

        init_u_to_v = AA_uv * self.deg[u]
        init_v_to_u = AA_uv * self.deg[v]
        #返回u对v 和v对u的亲密度
        return [init_u_to_v,init_v_to_u]


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

    #对于节点度相同的节点，如果它们的邻居不同，那么亲密度值也会不同，
    # 这可能导致一些节点被错误地归入不合适的社区中。为了避免这个问题，可以采用一些更加准确的亲密度指标，比如Katz指标或者SimRank指标。
    # chatGPT建议的使用simRank来计算亲密度 实验以后效果很差
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


    # Simulate the game
    # 在形成核心组的基础上再进行非合作博弈
    def community_detection_game(self, outdirpath, fname):
        NMI = -1.0
        max_NMI = -2.0
        maxit = 10  # 设置迭代次数为5 你当然可以设为10
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
        f_true = open("dataset/" + fname + "_com.dat")
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
        ARI = metrics.adjusted_rand_score(LA, LB)

        #Q的计算要把节点分成一个社区
        #比如parition = [[1,3,4,5,6],[8,54,33,12,44]] 里面一个[]就是一个社区
        #所以问题来了，你要把LA转化成partition才能直接用Q
        partition = self.Lables_to_Partition(LA) #LA是算法分区
        Q = modularity(self.G,partition)

        nmilist.append(NMI)
        arilist.append(ARI)
        Qlist.append(Q)

        if (max_NMI < NMI):
            max_NMI = NMI
            largest_NMI_itern = itern
            max_node_community = self.node_community.copy() #获得最佳社区结构到max_node_community 用NMI来评判最佳

        print("loop begin:")

        while itern < maxit: #开始博弈，实验maxit次
            itern += 1
            isChange = True
            nums = 0 #记录博弈多少次
            last_node = None #用来记录上一个节点的变量
            while isChange is True: #如果有改变就继续博弈
                #下面的代码问题是只要遇到一个不再改变自己收益函数的节点就停止博弈了，显然是有问题的。
                #但按照以往的经验达到纳什均衡的过程中，可能存在节点策略来回震荡的情况，需要多回合的博弈来稳定
                #但达到均衡后社区的精度并没有发生明显的提升，因此没有必要完全达到纳什均衡再停止
                #可以设置一个平衡节点，当平衡节点数量达到总节点的α倍就结束。
                node = random.choice(list(self.G.nodes())) #随机选择博弈节点
                # print("随机选择的节点是" + str(node))
                if last_node == node: #如果和上回合选的节点一样就没必要博弈了，重新选
                    continue
                else:
                    last_node = node #如果不一样就赋给last_node，继续记录下上一个节点是谁


                #用于纳什均衡的参数，当nochangeNum == self.node_count的时候 就是均衡了
                #TODO 每轮博弈都要重新归零来保证纳什均衡,但目前效果最差。为什么？？
                nochange_num = 0
                #尝试加入所有社区
                #得到所有社区集合,为了后续遍历所有社区
                community_set = []
                for node in self.G.nodes():
                    community_set.append(self.node_community[node])
                #随机顺序遍历相邻的社区，并尝试加入
                for c in community_set:
                    node_community = self.node_community[node]  # 取出博弈过程中变化的当前node社区
                    utility_node = self.utility_nodes[node]  # 博弈过程中节点的当前收益
                    if c == node_community: #如果c和节点的当前社区一致就没必要算了(本来就在一起，还加入什么),算下一个c
                        continue
                    #如果和当前社区不一样
                    utility_new = self.utility_function(node,c) #计算节点node加入社区c能获得的收益
                    if utility_new >= utility_node: #如果变大或者等于，则加入新的社区，等于是为了尽可能让节点形成社区，以防小社区的出现
                        self.node_community[node] = c #加入这个社区
                        self.utility_nodes[node] = utility_new #更新节点的收益
                        self.utility_list[node] = True #记录为True，节点的社区变化了
                    else:
                        self.utility_list[node] = False #如果没改变就记录为False

                #问题在这里，把所有节点都访问一次以后就可以结束了吗？？
                #应该是所有节点访问一圈都没有人选择改变策略 才是结束吧
                #nochange_num = 0 #没改变的数量，每轮都要重置为0，所以写在for外面，while里面
                for node in self.G.nodes():
                    #如果有一个等于True,就不能停止，继续博弈
                    if self.utility_list[node] == True:
                        isChange = True

                    # TODO: 为什么加上了这个纳什均衡效果 NMI反而差了？是代码有问题吗？还是就让他博弈次数多一点效果更好？
                    # TODO:另外Karate加不加博弈好像都没啥区别，说明Karate的社区在核心组形成后就没动了。34个节点都做不到NMI=1 想想办法！
                    # #如果这个节点没改变社区，那就计数
                    # 加入所有社区的话，如果不加上纳什均衡，跑大网络就无法收敛
                    else:
                        nochange_num = nochange_num + 1
                        if nochange_num == self.node_count: #如果全是Fasle，都没改变，那就是纳什均衡了。
                            isChange = False
                            print("我是纳什均衡停下来的")

                nums = nums + 1 #博弈的次数
                #
                if(nums == (5 * self.node_count)): #最多博弈次数到节点的5倍 就停止
                    isChange = False  # 所有节点都不改变了才是False
                    print("我是弈次数到节点的5倍就停下来的")


            newLA = [self.node_community[k] for k in self.input_node_community.keys()]
            print("博弈后newLA:" + str(newLA))
            NMI_LA_newLA = metrics.normalized_mutual_info_score(newLA,LA) #比较LA 和 newLA 有多少相似（改变）
            print("博弈后newLA对比LA的相似度(NMI)是:" + str(NMI_LA_newLA)) #用来比较博弈到底产生了多大作用

            NMI = metrics.normalized_mutual_info_score(newLA, LB)
            ARI = metrics.adjusted_rand_score(newLA, LB)

            partition = self.Lables_to_Partition(newLA)  # LA是算法分区
            Q = modularity(self.G,partition)

            nmilist.append(NMI)
            arilist.append(ARI)
            Qlist.append(Q)

            if (max_NMI < NMI):
                max_NMI = NMI
                largest_NMI_itern = itern
                max_node_community = self.node_community.copy() #记录下最佳NMI分区
            print("max_NMI:" + str(max_NMI))
            print("\n")

        print("loop done")

        self.node_community = max_node_community.copy()

        self.graph_result = defaultdict(list)

        for item in self.node_community.keys():
            node_comm = int(self.node_community[item])
            self.graph_result[node_comm].append(item)

        f = open(outdirpath + "/" + fname + ".txt", "w+")
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
        f.write("All NMI values: \n")
        f.write(str(nmilist))
        f.write("\n\n\n")
        f.write("All ARI values:     \n")
        f.write(str(arilist))
        f.write("\n\n\n")
        f.write("All Q values:     \n")
        f.write(str(Qlist))
        f.close()


    #收益函数1
    #计算节点u加入社区c能得到的收益
    def utility_function(self,u,c): # 节点u在社区c中的收益，即u与社区c中所有节点的亲密度之和
       paysoff_u = 0
       for node in self.G.nodes:
           # 如果节点在c中,计算与u的亲密度
           if self.node_community[node] == c:
               #不知道为什么报错，不影响运行
               list = self.simintimacy(u, node)
               paysoff_u = paysoff_u + 1/2 * (list[0] + list[1])
       return paysoff_u


    #收益函数2 明明看起来更复杂但这个收益函数比前面的要差
    #gain = 1/2m ∑(i,j) (Aijδ(i,j) - Intimacydidj/2m * |si ∩ sj|  δ(i,j)表示i.j是否有共同标签
    #loss = 1/2m (|si| - 1)
    def utility_linear_function(self,u,c): # 节点u在社区c中的收益
        gain_function = 0
        for neigh in self.G.neighbors(u): #Aij = 1
            community_neigh = self.node_community[neigh]
            community_node = self.node_community[u]

            deerta = 0
            # δ(i,j)表示i.j是否有共同标签
            if community_neigh != community_node:
                deerta = 0
            else:
                deerta = 1
            gain_function = 1/2 * self.edge_count * \
                            (1 * deerta - \
                            1/2 * (self.simintimacy(u,neigh)[0] + self.simintimacy(u,neigh)[1]) \
                             * self.deg[u] * self.deg[neigh] / 2 * self.edge_count * 1 )
                            # * (community_node & community_neigh) ) #正常是要取交集，但是这里单社区，直接数字1就行了

        # loss_function = 1/ 2 * self.edge_count * (len(self.node_community[u]) - 1) # 目前做单社区，那不能用len函数，其实就是1 没有损失
        loss_function = 0
        utility = gain_function - loss_function
        return utility

    # The internal degree of node v in a community 计算节点v在社区中的内在度in_v
    # 原来的作者当然还进行了更改
    def per(self, v):
        neiglist1 = self.G.neighbors(v)  #v节点的邻居列表
        in_v = 0
        self.nodecount_comm = defaultdict(int)
        for neig in neiglist1:
            if self.node_community[neig] == self.node_community[v]: #如果邻居与v处在同一社区
                in_v += 1 #in_v加一
            else: #否则把这个社区对应的key+1
                self.nodecount_comm[self.node_community[neig]] += 1
        cin_v = 1.0*in_v*in_v #最后对内在度进行平方
        per = cin_v
        return per


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