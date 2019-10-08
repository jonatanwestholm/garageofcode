import time
import numpy as np
import matplotlib.pyplot as plt

import networkx as nx
from networkx.algorithms.clique import find_cliques, find_cliques_recursive
from networkx.algorithms.clique import enumerate_all_cliques
from networkx.generators.classic import full_rary_tree
from networkx.generators.community import connected_caveman_graph, windmill_graph
from networkx.generators.harary_graph import hnm_harary_graph

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

def get_asymmetric_adj(G, comparison):
    node2deg = {u: len(G[u]) for u in G}
    node2deg = {u: (deg, i) for i, (u, deg) in enumerate(sorted(node2deg.items(), key=lambda x: x[1]))}
    adj = {} # adj[u] neighbours of u with higher degree
    for u in node2deg:
        d = node2deg[u]
        if comparison == "<":
            adj[u] = {v for v in G[u] if d < node2deg[v]}
        elif comparison == ">":
            adj[u] = {v for v in G[u] if d > node2deg[v]}
    return adj

def find_cliques_v001(G):
    if len(G) == 0:
        return iter([])

    adj = {u: {v for v in G[u] if v != u} for u in G}
    higher_degree_adj = get_asymmetric_adj(G, comparison="<")
    Q = []

    def get_cliques(cand, hdeg_adj_v):
        for u in cand & hdeg_adj_v:
            Q.append(u)
            cand_u = cand & adj[u]
            if not cand_u:
                yield Q[:]
            else:
                for clique in get_cliques(cand_u, higher_degree_adj[u]):
                    yield clique
            Q.pop()

    return get_cliques(set(G), set(G))

def find_cliques_v002(G):
    if len(G) == 0:
        return iter([])

    adj = {u: {v for v in G[u] if v != u} for u in G}

    higher_degree_adj = get_asymmetric_adj(G, comparison="<")
    lower_degree_adj  = get_asymmetric_adj(G, comparison=">")
    Q = []

    # Possible optimization: use the same thing as nx, 
    # if may be possible to know that some nodes will not
    # be part of a maximal clique. 

    def get_cliques(cand, cand_and_hdeg_adj_v):
        q = max(cand_and_hdeg_adj_v, key=lambda q: len(cand_and_hdeg_adj_v & higher_degree_adj[q]))
        for u in cand_and_hdeg_adj_v - higher_degree_adj[q]:
            # check if there is a node that dominates u
            # w dominates u if deg[w] < deg[u] and
            # adj[u] & cand <= adj[w] & cand
            #for w in cand & hdeg_adj_v & lower_degree_adj[u]:
            #    if not (node2cover[u] - node2cover[w]):
            #        dominated = True
            #        break
            #else:
            #    dominated = False
            #if dominated:
            #    continue
            Q.append(u)
            cand_u = cand & adj[u]
            if not cand_u:
                yield Q[:]
            else:
                cand_and_hdeg_adj_u = cand_u & higher_degree_adj[u]
                if cand_and_hdeg_adj_u:
                    for clique in get_cliques(cand_u, cand_and_hdeg_adj_u):
                        yield clique
            Q.pop()            

    #print("\t\tbranchings:", len(branchings))

    return get_cliques(set(G), set(G))

def test_clique_speed():
    np.random.seed(0)

    def len_iterator(func):
        return lambda G: sum(1 for _ in func(G))

    nx_iterative = len_iterator(find_cliques)
    nx_recursive = len_iterator(find_cliques_recursive)
    nx_all       = len_iterator(enumerate_all_cliques)
    custom       = len_iterator(find_cliques_v001)
    custom2      = len_iterator(find_cliques_v002)

    funcs = {
             #"nx all": nx_all,
             "nx iterative": nx_iterative,
             #"nx recursive": nx_recursive,
             "custom v001": custom,
             "custom v002:": custom2}

    t0 = time.time()
    params = {# custom algo is 30% faster for large random graphs
              "n=1e1, m=1e1": [get_random_graph(10, 0.1)],
              "n=1e2, m=1e2": [get_random_graph(100, 0.01)],
              "n=1e2, m=1e3": [get_random_graph(100, 0.1)],
              "n=1e3, m=1e3": [get_random_graph(1000, 0.001)],
              "n=1e3, m=1e4": [get_random_graph(1000, 0.01)],
              "n=1e3, m=1e5": [get_random_graph(1000, 0.1)],
              "n=1e3, m=2e5": [get_random_graph(1000, 0.2)],
              "caveman(100,10)": [connected_caveman_graph(100, 10)],
              "windmill(10, 10)": [windmill_graph(10, 10)],
              "nary_tree(3, 10000)": [full_rary_tree(2, 1000)],
              # custom algo is 20 times slower (!!) for harary_graphs
              # what makes these graphs special?
              # possibly: all nodes have (almost) the same degree, 
              #     no gain in sorting them
              #"harary(1e4, 1e5)": [hnm_harary_graph(10000, 100000)],
              #"n=1e3, m=1.5e5": [get_random_graph(1000, 0.15)],
              }
    t1 = time.time()
    #print("graph generation time: {0:.3f}".format(t1 - t0))

    benchmarking.run(funcs, params)

if __name__ == '__main__':
    if 1:
        test_clique_speed()
    elif 0:
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
    else:
        G = hnm_harary_graph(10, 40)        
        nx.draw_networkx(G)
        plt.show()
