# -*- coding: utf-8 -*-
import math
from collections import defaultdict
from sklearn import metrics
from networkx.algorithms.community.quality import modularity # 模块度 modularity(G,partition)
import networkx as nx
import random

'''

'''
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
       
        #Compute the core groups 从这里开始是构造核心组，你可以看看要不要在这上面继续改造。
        # 其实可以，参考A Four-Stage Algorithm for Community Detection Based on Label Propagation and Game Theory in Social Networks
        # 一开始快速形成一个初始社区有助于加速



        #那么他构造所谓的核心组，你也可以根据你的亲密度函数来构造你的"核心组"
        # 现在的做法是计算两个节点的平均亲密度。
        for node in self.G.nodes():
            #The degree of each node
            deg_node = self.deg[node]
            flag = True  #是否已标记核心组
            maxsimdeg = 0   #用于记录节点亲密度的最大值,每个节点都是从0开始的
            selected = node            
            if deg_node == 1: #如果节点的度为1，那么它的社区就是它唯一的那个邻居编号
                self.node_community[node] = self.node_community[list(self.G.neighbors(node))[0]]
            else:               #其他情况则遍历邻居 因为邻居的亲密度才有可能最大
                for neig in self.G.neighbors(node):                   
                    deg_neig = self.deg[neig]       #邻居的度
                    if flag is True and deg_node <= deg_neig: #Flag为true且当前节点的度小于等于邻居的度，那么他就可能会更改自己的核心组
                        flag = False #标记为false
                        break # 结束当前节点对邻居的遍历

                #判断flag是否为false，如果是true说明是度为1的节点，或者他是比所有邻居度都要大的节点，则遍历下一个节点
                if flag is False: #先判断一下flag是否为false
                    # 若为false,则按节点的邻居的编号顺序从小到大遍历
                    neighbors = sorted(self.G.neighbors(node))  # 按节点编号从小到大排序
                    for neig in neighbors:
                        #取邻居的度
                        deg_neig = self.deg[neig]
                        # Compute the intimacy coefficient
                        # Compute the node attraction 节点亲密度
                        nodesim_u_v = self.simintimacy(node, neig)[0]
                        nodesim_v_u = self.simintimacy(node, neig)[1]
                        nodesimdeg = (nodesim_u_v + nodesim_v_u) / 2
                        #如果算出来节点吸引力比以前的都要大
                        if nodesimdeg > maxsimdeg:
                            selected = neig #要选择的节点
                            maxsimdeg = nodesimdeg #更新最大值

                        #让当前节点加入根据亲密度选中节点的社区。
                        self.node_community[node] = self.node_community[selected]

        #1490节点 到这里都能正常运行

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
    def simintimacy(self,u,v):
        set_v = set(self.G.neighbors(v))
        set_u = set(self.G.neighbors(u))
        neighbors = set_v & set_u # u和v的公共邻居

        #AA指数
        AA_uv = 0.0

        #遍历公共邻居
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

    # Simulate the game
    # 在形成核心组的基础上再进行非合作博弈
    def community_detection_game(self, outdirpath, fname):
        NMI = -1.0
        max_NMI = -2.0
        maxit = 1  # 设置迭代次数为5 你当然可以设为10
        itern = 0 # 当前迭代回合

        largest_NMI_itern = 0  # 取得最大NMI的回合
        max_node_community = defaultdict(int)
        nmilist = []
        arilist = []
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
        nmilist.append(NMI)
        arilist.append(ARI)

        if (max_NMI < NMI):
            max_NMI = NMI
            largest_NMI_itern = itern
            max_node_community = self.node_community.copy() #获得最佳分区到max_node_community

        print("loop begin:")

        while itern < maxit: #开始博弈，实验maxit次
            itern += 1
            #随机选择博弈节点
            # for node in set(self.G.nodes()):
            isChange = True

            nums = 0 #记录跑了多少个节点
            last_node = None #用来记录上一个节点的变量
            while isChange is True: #如果有改变就继续博弈
                #下面的代码问题是只要遇到一个不再改变自己收益函数的节点就停止博弈了，显然是有问题的。
                #但按照以往的经验达到纳什均衡的过程中，可能存在节点策略来回震荡的情况，需要多回合的博弈来稳定
                #但达到均衡后社区的精度并没有发生明显的提升，因此没有必要完全达到纳什均衡再停止
                #可以设置一个平衡节点，当平衡节点数量达到总节点的α倍就结束。
                node = random.choice(list(self.G.nodes())) #随机选择博弈节点
                # print("随机选择的节点是" + str(node))
                if last_node == node: #如果和上回合选的一样就没必要博弈了，重新选
                    continue
                else:
                    last_node = node #如果不一样就赋给last_node，继续记录下上一个节点

                #尝试加入邻居社区
                neiglist = self.G.neighbors(node)
                communities_neigh = set()
                for neig in neiglist:
                    C = self.node_community[neig]
                    communities_neigh.add(C)

                #随机顺序遍历相邻的社区，并尝试加入
                for c in communities_neigh:

                    node_community = self.node_community[node]  # 取出博弈过程中变化的当前node社区
                    utility_node = self.utility_nodes[node]  # 博弈过程中节点的收益

                    if c == node_community: #如果c和节点的当前社区一致就没必要算了(本来就在一起，还加入什么),算下一个相邻的c
                        continue
                    utility_neig = self.utility_function(node,c) #计算节点node加入社区c能获得的收益
                    # utility_neig = self.utility_linear_function(node,c) #计算节点node加入社区c能获得的收益
                    if utility_neig > utility_node:
                        isChange = True #有节点的收益发生变化
                        self.node_community[node] = c #加入这个邻居社区
                        self.utility_nodes[node] = utility_neig #更新节点的收益

                #问题在这里，把所有节点都访问一次以后就可以结束了吗？？
                #应该是所有节点访问一圈都没有人选择改变策略 才是结束吧
                nums = nums + 1
                if(nums == self.node_count):
                    isChange = False  # 所有节点都不改变了才是False


            newLA = [self.node_community[k] for k in self.input_node_community.keys()]
            print("博弈后newLA:" + str(newLA))
            NMI_LA_newLA = metrics.normalized_mutual_info_score(newLA,LA) #比较LA 和 newLA 有多少相似（改变）
            print("博弈后newLA对比LA的相似度(NMI)是:" + str(NMI_LA_newLA)) #用来比较博弈到底产生了多大作用
            NMI = metrics.normalized_mutual_info_score(newLA, LB)
            ARI = metrics.adjusted_rand_score(newLA, LB)
            nmilist.append(NMI)
            arilist.append(ARI)

            if (max_NMI < NMI):
                max_NMI = NMI
                largest_NMI_itern = itern
                max_node_community = self.node_community.copy()
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
        f.close()

    def utility_function(self,u,c): # 节点u在社区c中的收益
       paysoff_u = 0
       u_community = self.node_community[u] #节点u的社区标签

       for v in self.G.neighbors(u):
           v_community = self.node_community[v]  # 节点v的社区标签
           if (v_community == c): #如果v在社区c中，那么才会计算收益
               list = self.simintimacy(u,v)

               #暂时是非重叠，那community标签就一个 int型不能用len函数
               # paysoff_u = paysoff_u + 1/2 * (list[0] / len(u_community) + list[1] / len(v_community)) * (u_community & v_community)
               paysoff_u = paysoff_u + 1/2 * (list[0] + list[1]) * (u_community & v_community)

       return paysoff_u


    #这个收益函数比前面的要差
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