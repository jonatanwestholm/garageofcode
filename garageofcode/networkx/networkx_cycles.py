import time
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt

import networkx as nx
from networkx.utils import arbitrary_element
from networkx.algorithms.cycles import simple_cycles

from garageofcode.common import benchmarking
from garageofcode.probing.utils import get_random_graph

def maximal_strongly_connected_components(G):
    """
    Slower than Tarjan's. Nevermind. 
    """
    while len(G):
        u = arbitrary_element(G)
        decendants = _reachable_from(G, u)
        ancestors = _reachable_from(G._pred, u)
        scc = decendants & ancestors
        yield scc
        if len(scc) > 1:
            print(scc)
        G = G.subgraph(set(G) - scc)


def _reachable_from(G, u):
    visited = set([u])
    stack = [u]
    unvisited = len(G) - 1
    while stack:
        node = stack.pop()
        for v in G[node]:
            if not v in visited:
                visited.add(v)
                stack.append(v)
                unvisited -= 1
                if not unvisited:
                    return visited
    return visited


def test_cycle_speed():
    np.random.seed(0)

    def len_iterator(func):
        return lambda G: sum(1 for _ in func(G))

    nx_iterative = len_iterator(simple_cycles)
    custom1      = len_iterator(simple_cycles_v001)

    funcs = {
             "networkx": nx_iterative,
             "v001": custom1,
             }

    t0 = time.time()
    params = {
              #"star(3)": [star_graph(4)],
              "n=1e1, m=1e1": [get_random_graph(10, 0.1, directed=True)],
              "n=1e2, m=1e2": [get_random_graph(100, 0.01, directed=True)],
              "n=1e2, m=1.7e2": [get_random_graph(100, 0.017, directed=True)],
              #"n=1e3, m=1.4e3": [get_random_graph(1000, 0.0014, directed=True)],
              "n=1e3, m=1e3": [get_random_graph(1000, 0.0026, directed=True)],
              #"n=1e3, m=1e5": [get_random_graph(1000, 0.1, directed=True)],
              #"n=1e3, m=2e5": [get_random_graph(1000, 0.2)],
              #"caveman(100,10)": [connected_caveman_graph(100, 10)],
              #"windmill(10, 10)": [windmill_graph(10, 10)],
              #"nary_tree(3, 1000)": [full_rary_tree(2, 1000)],
              #"complete(20)": [complete_graph(20)],
              }
    t1 = time.time()
    #print("graph generation time: {0:.3f}".format(t1 - t0))

    benchmarking.run(funcs, params)


if __name__ == '__main__':
    test_cycle_speed()