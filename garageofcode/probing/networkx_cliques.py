import time
import numpy as np
import matplotlib.pyplot as plt

import networkx as nx
from networkx.algorithms.clique import find_cliques, find_cliques_recursive
from networkx.algorithms.clique import enumerate_all_cliques

from garageofcode.probing.utils import get_random_graph
import garageofcode.common.benchmarking as benchmarking

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

def get_asymmetric_adj(G):
    node2deg = {u: len(G[u]) for u in G}
    node2deg = {u: (deg, i) for i, (u, deg) in enumerate(sorted(node2deg.items(), key=lambda x: x[1]))}
    adj = {} # adj[u] neighbours of u with higher degree
    for u in node2deg:
        d = node2deg[u]
        adj[u] = {v for v in G[u] if node2deg[v] > d}
    return adj

def find_cliques_v001(G):
    if len(G) == 0:
        return iter([])

    adj = {u: {v for v in G[u] if v != u} for u in G}
    assym_adj = get_asymmetric_adj(G)
    Q = []

    def get_cliques(cand, assym_adj_v):
        if not cand:
            yield Q[:]
        for u in cand & assym_adj_v:
            Q.append(u)
            cand_u = cand & adj[u]
            for clique in get_cliques(cand_u, assym_adj[u]):
                yield clique
            Q.pop()

    return get_cliques(set(G), set(G))

def test_clique_speed():
    np.random.seed(0)

    nx_iterative = lambda G: sum(1 for _ in find_cliques(G))
    nx_recursive = lambda G: sum(1 for _ in find_cliques_recursive(G))
    nx_all       = lambda G: sum(1 for _ in enumerate_all_cliques(G))
    custom       = lambda G: sum(1 for _ in find_cliques_v001(G))

    funcs = {
             #"nx all": nx_all,
             "nx iterative": nx_iterative,
             #"nx recursive": nx_recursive,
             "custom": custom}

    t0 = time.time()
    params = {"n=1e1, m=1e1": [get_random_graph(10, 0.1)],
              "n=1e2, m=1e2": [get_random_graph(100, 0.01)],
              "n=1e2, m=1e3": [get_random_graph(100, 0.1)],
              "n=1e3, m=1e3": [get_random_graph(1000, 0.001)],
              "n=1e3, m=1e4": [get_random_graph(1000, 0.01)],
              "n=1e3, m=1e5": [get_random_graph(1000, 0.1)],
              "n=1e3, m=1.5e5": [get_random_graph(1000, 0.15)],
              "n=1e3, m=2e5": [get_random_graph(1000, 0.2)],}
    t1 = time.time()
    #print("graph generation time: {0:.3f}".format(t1 - t0))

    benchmarking.run(funcs, params)

if __name__ == '__main__':
    if 1:
        test_clique_speed()
    else:
        G = get_random_graph(10, 0.4)
        node2deg = {u: len(G[u]) for u in G}
        for k, v in node2deg.items():
            print(k, v)

        for clique in find_cliques(G):
            print(clique)

        print()

        for clique in find_cliques_v001(G):
            print(clique)

        nx.draw_networkx(G)
        plt.show()
