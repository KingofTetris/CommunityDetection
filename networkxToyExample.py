import networkx as nx

G = nx.Graph()

G.add_node('A',role = 'teacher')
G.add_node('B',role = 'student')
G.add_node('C',role = 'manager')
G.add_edge('A','B',weight = 6,relation = 'family')
G.add_edge('A','C',weight = 1)
G.add_edge('B','C',weight = 4)
nx.draw_networkx(G)

# print(G.degree) #[('A', 2), ('B', 2), ('C', 2)]
#
# print(G.nodes) #['A', 'B', 'C']
# print(G.nodes(data=True)) #[('A', {'role': 'teacher'}), ('B', {'role': 'student'}), ('C', {'role': 'manager'})]
# print(G.edges) #[('A', 'B'), ('A', 'C'), ('B', 'C')]
# print(G.edges(data=True)) #[('A', 'B', {'weight': 6, 'relation': 'family'}), ('A', 'C', {'weight': 1}), ('B', 'C', {'weight': 4})]
#
# print(G.nodes['A']['role']) #边直接取，点要先取nodes 结果是:teacher
# print(G['A']['B']) #{'weight': 6, 'relation': 'family'}
# print(G['A']['B']['weight']) # 6

for node in G.nodes():
    print(node)
    print(type(node))

#节点按度降序
for tup in sorted(G.degree,key = lambda x:x[1],reverse=True):
    print(tup)
    print(tup[0])

# from networkx.algorithms import bipartite
# B = nx.Graph()
# B.add_nodes_from(['A', 'B', 'C', 'D', 'E'],bipartite=0) #告诉图0在左边，1在右边
# B.add_nodes_from([1,2,3,4],bipartite=1)
# B.add_edges_from([('A', 1), ('B', 1), ('C', 1), ('C', 3), ('D', 2), ('E', 3), ('E', 4)])
# print(bipartite.is_bipartite(B))
#
# import networkx as nx
# from networkx.algorithms import bipartite
# B = nx.Graph()
# list = [('A', 1), ('B', 1),
# ('C', 1), ('D', 1), ('H', 1), ('B', 2), ('C', 2),
# ('D', 2), ('E', 2), ('G', 2), ('E', 3), ('F', 3), ('H', 3),
# ('J', 3), ('E', 4), ('I', 4), ('J', 4)]
# B.add_edges_from(list)
# X = set(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'])
# P = bipartite.projected_graph(B, X)
# Y = set([1, 2, 3, 4])
# O = bipartite.weighted_projected_graph(B, Y) #weighted_projected 显示权重
# nx.draw_networkx(B)
# nx.draw_networkx(P)
# nx.draw_networkx(O)
