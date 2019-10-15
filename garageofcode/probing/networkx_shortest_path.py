import time
import numpy as np

import networkx as nx
from networkx import all_pairs_shortest_path_length
from networkx.generators.atlas import _generate_graphs
from networkx.generators.classic import full_rary_tree, complete_graph, star_graph
from networkx.generators.community import connected_caveman_graph, windmill_graph
from networkx.generators.harary_graph import hnm_harary_graph

from garageofcode.common import benchmarking
from garageofcode.probing.utils import get_random_graph

def test_sp_speed():
    np.random.seed(0)

    def total_length_all_paths(func, dev):
        return lambda G: sum(sum(sum(d for v, d in u2sp.items())
                                            for u, u2sp in func(G, dev=dev)) 
                                                for _ in range(1))

    sp = total_length_all_paths(all_pairs_shortest_path_length, "current")
    sp_set = total_length_all_paths(all_pairs_shortest_path_length, "set")
    sp_check = total_length_all_paths(all_pairs_shortest_path_length, "set+check")
    sp_opt = total_length_all_paths(all_pairs_shortest_path_length, "queue")

    funcs = {
             "current": sp,
             "set": sp_set,
             #"set+check": sp_check,
             "pull request": sp_opt,
             }

    params = {
              #"star(3)": [star_graph(4)],
              "n=1e1, m=1e1": [get_random_graph(10, 0.2, directed=True)],
              "n=1e1, m=3e1": [get_random_graph(10, 0.6, directed=True)],
              "n=1e2, m=1e2": [get_random_graph(100, 0.02, directed=True)],
              "n=1e3, m=1.4e3": [get_random_graph(1000, 0.0014, directed=True)],
              "n=1e3, m=1e3": [get_random_graph(1000, 0.002, directed=True)],
              "n=1e3, m=1e4": [get_random_graph(1000, 0.02, directed=True)],
              #"n=1e3, m=1e5": [get_random_graph(1000, 0.2, directed=True)],
              #"n=1e4, m=1e6": [get_random_graph(10000, 0.02, directed=True)],
              #"n=1e4, m=1e7": [get_random_graph(10000, 0.2, directed=True)],
              "caveman(100,10)": [nx.DiGraph(connected_caveman_graph(100, 10))],
              "windmill(10, 10)": [nx.DiGraph(windmill_graph(10, 10))],
              "nary_tree(3, 1000)": [nx.DiGraph(full_rary_tree(2, 1000))],
              "complete(100)": [nx.DiGraph(complete_graph(100))],
              "mlp(10, 10)": [mlp_graph(10, 10)],
              "mlp(10, 100)": [mlp_graph(10, 100)],
              "amnesia(100, 100)": [amnesia_graph(100, 100)],
              }

    # the atlas graphs are not large enough to be interesting benchmarks
    num_atlas = 0
    atlas_graphs = [nx.DiGraph(G) 
                    for _, G in zip(range(num_atlas), _generate_graphs())]
    atlas_graphs = atlas_graphs[1:] # first graph is empty
    atlas_graphs = [rename_nodes(G) for G in atlas_graphs]
    atlas = {"atlas{}".format(i): [G] for i, G in enumerate(atlas_graphs)}
    params.update(atlas)

    benchmarking.run(funcs, params, validate=False, decimals=2)


def rename_nodes(G):
    """
    Rename nodes in G to integer indexes, starting on 0.
    Arbitrary order.
    """
    node2idx = {node: i for i, node in enumerate(G)}
    H = type(G)()

    for u in G:
        H.add_node(node2idx[u])

    for u, v in G.edges:
        H.add_edge(node2idx[u], node2idx[v])

    return H


def mlp_graph(k, n):
    """
    A graph with k layers and n nodes in each layer.
    Each layer is fully connected (directed edges) to the next.
    MLP = multilayer perceptron, simple neural network
    """
    G = nx.DiGraph()

    for layer in range(k - 1):
        i0 = n * layer
        j0 = n * (layer + 1)
        for i in range(n):
            for j in range(n):
                G.add_edge(i0 + i, j0 + j)

    return G


def amnesia_graph(n, b):
    """
    n nodes in a directed cycle
    all n nodes are connected to all b nodes (directed edges)
    all b nodes independent
    """

    G = nx.DiGraph()
    b0 = n

    for i in range(n):
        G.add_edge(i, (i + 1) % n)
        for bi in range(b0, b0 + b):
            G.add_edge(i, bi)

    return G


if __name__ == '__main__':
    test_sp_speed()
