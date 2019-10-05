import networkx as nx
from networkx.algorithms.flow.preflowpush import preflow_push

G = nx.Graph()

s = "s"
t = "t"

G.add_edge(s, 1, capacity=16)
G.add_edge(s, 2, capacity=13)
G.add_edge(1, 2, capacity=4)
G.add_edge(1, 3, capacity=12)
G.add_edge(2, 3, capacity=9)
G.add_edge(2, 4, capacity=14)
G.add_edge(3, 4, capacity=7)
G.add_edge(3, t, capacity=20)
G.add_edge(4, t, capacity=4)


R = preflow_push(G, s, t)
print("Flow:", R.graph["flow_value"])
for u, v, flow in R.edges(data="flow"):
    if flow >= 0:
        print("({} -> {}):".format(u, v), flow)