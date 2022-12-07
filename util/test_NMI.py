import networkx as nx
import math

class Evaluate:
    """
    社区划分结果评估
    """

    def __init__(self, G, cur_community, real_community):
        """
        评价指标初始化
        :param G: 图
        :param cur_community: 当前社区划分结果 {id： nodes}
        :param real_community: 真实社区结果{id : nodes}
        :return: null
        """
        self.G = G
        self.cur_community = cur_community
        self.real_community = real_community


    def Q(self):
        """
        计算划分社区的模块度Q(modularity)
        未知和已知社区的评估指标
        :return: Q_value
        """
        nodes_number = self.G.number_of_nodes()
        edges_number = self.G.number_of_edges()
        Q_value = 0
        for key in self.cur_community.keys():
            #社区c
            c = self.cur_community[key]
            #社区内结点度数之和
            degrees = 0
            #社区内部边的总数
            inter_edges = 0
            for u in c:
                u_neighbors = set(nx.all_neighbors(self.G, u))
                degrees += len(u_neighbors)
                for nbr in u_neighbors:
                    if nbr in c:
                        inter_edges += 1
            #因为是无向图，所以边数要除以2
            inter_edges /= 2
            #cq = inter_edges / edges_number - math.pow(degrees / (2 * edges_number), 2)
            cq = inter_edges / edges_number - (degrees / (2 * edges_number)) ** 2
            Q_value += cq
        return Q_value


    def NMI(self):
        """
        标准化互信息值( Normalized mutual information)
        已知真实社区划分结果的评价指标
        行代表真实社区划分（real_community）
        列代表当前社区划分结果(cur_community)
        :return:NMI_value
        """
        nodes_number = self.G.number_of_nodes()
        r_id = [key for key in self.real_community]
        c_id = [key for key in self.cur_community]
        #分子
        sum_rc = 0
        #分母两项之和
        sum_r = sum_c = 0

        for i in range(0, len(r_id)):
            temp = 0
            nodes_i = set(self.real_community[r_id[i]])
            for j in range(0, len(c_id)):
                nodes_j = set(self.cur_community[c_id[j]])
                common = nodes_i & nodes_j
                a = len(common) * nodes_number / (len(nodes_i) * len(nodes_j))
                if a > 0:
                    temp += len(common) * math.log10(a)
            sum_rc += temp

        for i in range(0, len(r_id)):
            nodes_i = set(self.real_community[r_id[i]])
            sum_r += len(nodes_i) * math.log10(len(nodes_i) / nodes_number)
        for j in range(0, len(c_id)):
            nodes_j = set(self.cur_community[c_id[j]])
            sum_c += len(nodes_j) * math.log10(len(nodes_j) / nodes_number)

        sum_rc = sum_rc * (-2)
        NMI_value = sum_rc / (sum_r + sum_c)
        return NMI_value
