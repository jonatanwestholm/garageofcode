import time
import numpy as np

import networkx as nx
from networkx.algorithms.components.strongly_connected import is_strongly_connected

from garageofcode.common import benchmarking
from garageofcode.probing.utils import get_random_graph

def is_strongly_connected_v001(G):
    marcos = set([])
    count = 0
    for u in set(G):
        if u in marcos:
            continue
        count += 1
        if is_marco_polo(G, u):
            marcos.update(backsearch(G, u))
        else:
            return False
    print()
    print("num marco_polo searches:", count)
    print()
    return True

def backsearch(G, u):
    visited = set([u])
    unvisited = set(G) - visited
    stack = [u]
    while stack:
        node = stack.pop()
        for v in G._pred[node]:
            if not v in visited:
                visited.add(v)
                unvisited.remove(v)
                stack.append(v)
                if not unvisited:
                    return visited
    return visited

def is_marco_polo(G, u):
    unvisited = set(G)
    stack = [u]
    while stack:
        node = stack.pop()
        for v in G[node]:
            if v in unvisited:
                unvisited.remove(v)
                stack.append(v)
                if not unvisited:
                    return True
    return False


def test_scc_speed():
    np.random.seed(0)

    def len_iterator(func):
        return lambda G: sum(1 for _ in func(G))

    nx_iterative = is_strongly_connected
    custom1      = is_strongly_connected_v001

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
              "n=1e3, m=1.4e3": [get_random_graph(1000, 0.0014, directed=True)],
              "n=1e3, m=1e3": [get_random_graph(1000, 0.0026, directed=True)],
              "n=1e3, m=1e5": [get_random_graph(1000, 0.1, directed=True)],
              "n=1e4, m=2e6": [get_random_graph(10000, 0.2, directed=True)],
              #"caveman(100,10)": [connected_caveman_graph(100, 10)],
              #"windmill(10, 10)": [windmill_graph(10, 10)],
              #"nary_tree(3, 1000)": [full_rary_tree(2, 1000)],
              #"complete(20)": [complete_graph(20)],
              }
    t1 = time.time()
    #print("graph generation time: {0:.3f}".format(t1 - t0))

    benchmarking.run(funcs, params)


if __name__ == '__main__':
    test_scc_speed()