import networkx as nx
import numpy as np

def FSA(G, alpha, beta):
    # 计算平均距离
    n = G.number_of_nodes()
    avd = 2 / (n * (n-2)) * sum([sum(nx.shortest_path_length(G, u).values()) for u in G.nodes()])
    # 初始化
    node_degree = dict(G.degree())
    sorted_nodes = sorted(node_degree.items(), key=lambda x: x[1], reverse=True)
    important_nodes = [sorted_nodes[0][0]]
    community = {n: 0 for n in G.nodes()}
    community[sorted_nodes[0][0]] = 1
    # 计算重要节点
    for node, degree in sorted_nodes[1:]:
        for c in important_nodes:
            if nx.shortest_path_length(G, node, c) < avd:
                break
        #如果都>=avd
        community[node] = node
        # 对于那些还没有社区的节点
        if community[node] == 0:
            community[node] = max(community.values()) + 1
            important_nodes.append(node)
    # 合作博弈
    num_edges = G.number_of_edges()
    while True:
        max_utility = -np.inf
        max_pair = None
        for i in range(len(important_nodes)):
            for j in range(i+1, len(important_nodes)):
                if community[important_nodes[i]] == community[important_nodes[j]]:
                    continue
                merged_community = list(set(G.neighbors(important_nodes[i])) | set(G.neighbors(important_nodes[j])) | {important_nodes[i], important_nodes[j]})
                edges_in_merged_community = G.subgraph(merged_community).number_of_edges()
                degree_in_merged_community = sum([node_degree[n] for n in merged_community])
                utility = edges_in_merged_community/num_edges - (degree_in_merged_community/(2*num_edges))**2
                if utility > max_utility:
                    max_utility = utility
                    max_pair = (important_nodes[i], important_nodes[j])
        if max_utility <= 0:
            break
        new_community_label = min(community.values()) - 1
        for node in G.nodes():
            if community[node] == community[max_pair[0]] or community[node] == community[max_pair[1]]:
                community[node] = new_community_label
        important_nodes.remove(max_pair[0])
        important_nodes.remove(max_pair[1])
        important_nodes.append(new_community_label)
        community[max_pair[0]] = new_community_label
        community[max_pair[1]] = new_community_label
    # 非合作博弈
    for i in range(len(important_nodes)):
        x = important_nodes[i]
        while True:
            max_utility = -np.inf
            new_community_label = community[x]
            for c in range(1, max(community.values())+1):
                if c == community[x]:
                    continue
                nodes_in_c = [node for node in G.nodes() if community[node] == c]
                edges_in_c = G.subgraph(nodes_in_c).number_of_edges()
                degree_of_x = node_degree[x]
                utility = edges_in_c/degree_of_x
                if utility > max_utility:
                    max_utility = utility
                    new_community_label = c
            if new_community_label == community[x]:
                break
            community[x] = new_community_label
