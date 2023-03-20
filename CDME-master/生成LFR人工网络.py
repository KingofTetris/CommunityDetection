from networkx.generators.community import LFR_benchmark_graph
G = LFR_benchmark_graph(n=1000, tau1=1.5, tau2=1.5, mu=0.5, average_degree=5.0, min_degree=1,min_community=20, seed=10)
communities = {frozenset(G.nodes[v]["community"]) for v in G}
print(communities)