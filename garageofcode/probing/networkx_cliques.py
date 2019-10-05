import time

import networkx as nx
from networkx.algorithms.clique import find_cliques, find_cliques_recursive


def test_complete_graph():
    G = nx.Graph()

    n = 10
    for i in range(n):
        for j in range(i+1, n):
            G.add_edge(i, j)

    t0 = time.time()
    for clique in find_cliques_recursive(G):
        print(clique)
    print("Total time:", time.time() - t0)
