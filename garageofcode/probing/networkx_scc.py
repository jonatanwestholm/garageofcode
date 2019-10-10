import numpy as np

import networkx as nx
from networkx import is_strongly_connected, is_strongly_connected_dev

from garageofcode.common import benchmarking
from garageofcode.probing.utils import get_random_graph

def is_strongly_connected_v001(G):
    N = len(G)
    u = next(iter(G))
    #return len(reachable_from(G, u)) == N and \
    #       len(reachable_from(G._pred, u)) == N
    #G_reverse = G.reverse()
    return len(nx.descendants(G, u) | {u}) == N and \
           len(nx.ancestors(G, u) | {u}) == N


def reachable_from(G, u):
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


def test_scc_speed():
    np.random.seed(0)

    def len_iterator(func):
        return lambda G: sum(1 for _ in func(G))

    nx_master    = is_strongly_connected
    nx_dev       = is_strongly_connected_dev
    custom1      = is_strongly_connected_v001

    funcs = {
             "networkx": nx_master,
             "networkx dev": nx_dev,
             "v001": custom1,
             }

    params = {
              #"star(3)": [star_graph(4)],
              "n=1e1, m=1e1": [get_random_graph(10, 0.1, directed=True)],
              "n=1e2, m=1e2": [get_random_graph(100, 0.01, directed=True)],
              "n=1e2, m=1.7e2": [get_random_graph(100, 0.017, directed=True)],
              "n=1e3, m=1.4e3": [get_random_graph(1000, 0.0014, directed=True)],
              "n=1e3, m=1e3": [get_random_graph(1000, 0.0026, directed=True)],
              "n=1e3, m=1e5": [get_random_graph(1000, 0.1, directed=True)],
              #"n=1e4, m=2e6": [get_random_graph(10000, 0.2, directed=True)],
              #"caveman(100,10)": [connected_caveman_graph(100, 10)],
              #"windmill(10, 10)": [windmill_graph(10, 10)],
              #"nary_tree(3, 1000)": [full_rary_tree(2, 1000)],
              #"complete(20)": [complete_graph(20)],
              }

    benchmarking.run(funcs, params)


if __name__ == '__main__':
    test_scc_speed()