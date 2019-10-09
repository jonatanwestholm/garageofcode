import networkx as nx

G = nx.DiGraph()

G.add_edge(1, 2)
G.add_edge(1, 3)
#G.add_edge(2, 4)
G.add_edge(2, 3)

print("Is aperiodic:", nx.is_aperiodic(G))