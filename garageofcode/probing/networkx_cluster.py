import time
import numpy as np
import matplotlib.pyplot as plt
from itertools import product

import networkx as nx
from networkx.algorithms.cluster import _directed_triangles_and_degree_iter, _triangles_and_degree_iter

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

def find_triangles(G):
    """
    Assume undirected
    Assume no self-edges
    """
    node2deg = {u: (len(G[u]), i) for i, u in enumerate(G)}
    adj = {u: {v for v in G[u]} for u in G}

    num_triangles = 0
    for u in G:
        d = node2deg[u]
        neighbours = adj[u]
        more_central = [v for v in G[u] if node2deg[v] > d]
        for v in more_central:
            num_triangles += len(neighbours & adj[v])
            '''
            for w in more_central[j+1:]:
                if w in G[v]:
                    num_triangles += 1
            '''

    return num_triangles / 3


def test_triangle_speed():
    np.random.seed(0)
    G = nx.Graph()

    n = 10000
    rate = 0.001

    for i in range(n):
        G.add_node(i)

    for i in range(n):
        for j in range(i+1, n):
            if np.random.random() < rate:
                G.add_edge(i, j)

    accuracy = 5

    t0 = time.time()
    num_triangles = find_triangles(G)
    t1 = time.time()
    print("custom answer:", num_triangles)
    print("custom time: {0:.{1:d}f}".format(t1 - t0, accuracy))

    t0 = time.time()
    num_triangles = 0
    for _, _, ntriangles, _ in _triangles_and_degree_iter(G):
        num_triangles += ntriangles

    t1 = time.time()
    print("networkx answer:", num_triangles / 6)
    print("networkx time: {0:.{1:d}f}".format(t1 - t0, accuracy))

if __name__ == '__main__':
    test_triangle_speed()