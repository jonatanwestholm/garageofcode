import time
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
from multiprocessing import Pool

import networkx as nx
from networkx.algorithms.cluster import _directed_triangles_and_degree_iter
from networkx.algorithms.cluster import _triangles_and_degree_iter

import garageofcode.common.benchmarking as benchmarking

def test_count_directed_triangles():
    """
    It appears that _directed_triangles_and_degree_iter
    treats the graph as if the edges were undirected.
    In other words, it counts also triangles that are not cycles.
    """
    G = nx.DiGraph()

    # this graph has no cycles, but apparently it has two 'directed triangles'
    G.add_edge(1, 2)
    G.add_edge(2, 3)
    G.add_edge(1, 3)

    #G.add_edge(2, 4)
    #G.add_edge(1, 4)

    for node, total_degree, reciprocal_degree, directed_triangles in \
                                _directed_triangles_and_degree_iter(G, nodes=1):
        print("node:", node)
        print("total_degree:", total_degree)
        print("reciprocal_degree:", reciprocal_degree)
        print("directed_triangles:", directed_triangles)

    nx.draw_networkx(G)
    plt.show()

def find_triangles_v002(G):
    """
    Set-intersection to replace innermost loop
    """
    node2deg = {u: (len(G[u]), i) for i, u in enumerate(G)}
    adj = {u: {v for v in G[u]} for u in G}

    num_triangles = 0
    for u in G:
        d = node2deg[u]
        neighbours = adj[u]
        more_central = [v for v in neighbours if node2deg[v] > d]
        for v in more_central:
            num_triangles += len(neighbours & adj[v])
            '''
            for w in more_central[j+1:]:
                if w in G[v]:
                    num_triangles += 1
            '''

    return num_triangles / 3

def find_triangles_v003(G):
    """
    Pre-sort nodes to favour low-degree nodes
    """
    adj = get_asymmetric_adj(G)

    num_triangles = 0
    for u in G:
        adj_u = adj[u]
        for v in adj_u:
            num_triangles += len(adj_u & adj[v])
    
    return num_triangles
    
    # is a little slower because of extra dict lookups
    # parallelism isn't used
    #return sum(sum(len(adj[u] & adj[v]) for v in adj[u]) for u in G)


def find_triangles_v004(G):
    """
    Attempt to use parallelism - is much much slower, 
    because I can't find a good variable scope for adj.
    """
    nodes = [u for u in G]
    node2deg = {u: len(G[u]) for u in G}
    node2deg = {u: (deg, i) for i, (u, deg) in enumerate(sorted(node2deg.items(), key=lambda x: x[1]))}
    adj = {} # adj[u] neighbours of u with higher degree
    for u in node2deg:
        d = node2deg[u]
        adj[u] = {v for v in G[u] if node2deg[v] > d}

    adjs = [(adj[u], adj) for u in G]

    with Pool(4) as p:
        return sum(p.map(u2ntriangles, adjs))

def u2ntriangles(adjs):
    adj_u, adj = adjs
    return sum(len(adj_u & adj[v]) for v in adj_u)


def get_asymmetric_adj(G):
    node2deg = {u: len(G[u]) for u in G}
    node2deg = {u: (deg, i) for i, (u, deg) in enumerate(sorted(node2deg.items(), key=lambda x: x[1]))}
    adj = {} # adj[u] neighbours of u with higher degree
    for u in node2deg:
        d = node2deg[u]
        adj[u] = {v for v in G[u] if node2deg[v] > d}
    return adj

def find_quadrangles_v001(G):
    """
    Pre-sort nodes to favour low-degree nodes
    Incorrect, it only finds ordered quadrangles!
    For example, the path 1 -> 2 -> 4 -> 3 -> 1 will not be found
    """
    adj = get_asymmetric_adj(G)

    num_quadrangles = 0
    for u in G:
        adj_u = adj[u]
        for v in adj_u:
            adj_v = adj[v]
            for w in adj_v:
                num_quadrangles += len(adj_u & adj[w])
    
    return num_quadrangles       


def get_random_graph(n, rate):
    G = nx.Graph()

    for i in range(n):
        G.add_node(i)

    for i in range(n):
        if 1: # faster for large, sparse graphs
            num_larger = n - 1 - i
            for j in np.random.choice(range(i + 1, n), min(int(n * rate), num_larger), replace=False):
                if i != j:
                    G.add_edge(i, j)
        else:
            for j in range(i+1, n):
                if np.random.random() < rate:
                    G.add_edge(i, j)

    return G

def networkx_find_triangles(G):
    num_triangles = 0
    for _, _, ntriangles, _ in _triangles_and_degree_iter(G):
        num_triangles += ntriangles
    return num_triangles // 6    
    
def test_triangle_speed():
    np.random.seed(0)

    funcs = {"networkx": networkx_find_triangles, 
             "custom v002": find_triangles_v002,
             "custom v003": find_triangles_v003}

    t0 = time.time()
    params = {"n=1e2, m=1e3": [get_random_graph(100, 0.1)],
              "n=1e3, m=1e4": [get_random_graph(1000, 0.01)],
              "n=1e3, m=1e5": [get_random_graph(1000, 0.1)],
              "n=1e4, m=1e5": [get_random_graph(10000, 0.01)],}
    t1 = time.time()
    print("graph generation time: {0:.3f}".format(t1 - t0))

    benchmarking.run(funcs, params)


if __name__ == '__main__':
    test_triangle_speed()
