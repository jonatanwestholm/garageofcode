import time
import numpy as np

import networkx as nx
from networkx import descendants, descendants_dev
from networkx import ancestors, ancestors_dev
from networkx.generators.atlas import _generate_graphs
from networkx.generators.classic import full_rary_tree, complete_graph, star_graph
from networkx.generators.community import connected_caveman_graph, windmill_graph
from networkx.generators.harary_graph import hnm_harary_graph

from garageofcode.common import benchmarking
from garageofcode.probing.utils import get_random_graph

def test_dag_speed():
    np.random.seed(0)

    def activate_from(func):
        return lambda G, u: len(func(G, u))

    des     = activate_from(descendants)
    des_dev = activate_from(descendants_dev)
    anc     = activate_from(ancestors)
    anc_dev = activate_from(ancestors_dev)

    funcs = {
             #"des dev": des_dev,
             #"des current": des,
             "caching": anc,
             "anc dev": anc_dev,
             "anc current": anc,
             }

    params = {
              #"star(3)": [star_graph(4)],
              "n=1e1, m=1e1": [get_random_graph(10, 0.2, directed=True), 0],
              "n=1e2, m=1e2": [get_random_graph(100, 0.02, directed=True), 0],
              #"n=1e2, m=1.7e2": [get_random_graph(100, 0.017, directed=True)],
              #"n=1e3, m=1.4e3": [get_random_graph(1000, 0.0014, directed=True)],
              "n=1e3, m=1e3": [get_random_graph(1000, 0.002, directed=True), 0],
              "n=1e3, m=1e5": [get_random_graph(1000, 0.2, directed=True), 0],
              #"n=1e4, m=1e6": [get_random_graph(10000, 0.02, directed=True), 0],
              #"n=1e4, m=1e7": [get_random_graph(10000, 0.2, directed=True)],
              "caveman(100,10)": [nx.DiGraph(connected_caveman_graph(100, 10)), 0],
              "windmill(10, 10)": [nx.DiGraph(windmill_graph(10, 10)), 0],
              "nary_tree(3, 1000)": [nx.DiGraph(full_rary_tree(2, 1000)), 0],
              "complete(100)": [nx.DiGraph(complete_graph(100)), 0],
              }

    # the atlas graphs are not large enough to be interesting benchmarks
    num_atlas = 0
    atlas_graphs = [nx.DiGraph(G) 
                    for _, G in zip(range(num_atlas), _generate_graphs())]
    atlas_graphs = atlas_graphs[1:] # first graph is empty
    atlas_graphs = [rename_nodes(G) for G in atlas_graphs]
    atlas = {"atlas{}".format(i): [G, 0] for i, G in enumerate(atlas_graphs)}
    params.update(atlas)

    benchmarking.run(funcs, params, decimals=2)

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

if __name__ == '__main__':
    test_dag_speed()
