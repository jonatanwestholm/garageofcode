import time
import numpy as np

import networkx as nx
from networkx import descendants, descendants_dev
from networkx import ancestors, ancestors_dev

from garageofcode.common import benchmarking
from garageofcode.probing.utils import get_random_graph

def test_dag_speed():
    np.random.seed(0)

    def activate_from(func):
        return lambda G: len(func(G, 0))

    des     = activate_from(descendants)
    des_dev = activate_from(descendants_dev)
    anc     = activate_from(ancestors)
    anc_dev = activate_from(ancestors_dev)

    funcs = {
             #"des current": des,
             #"des dev": des_dev,
             "anc current": anc,
             "anc dev": anc_dev,
             }

    params = {
              #"star(3)": [star_graph(4)],
              "n=1e1, m=1e1": [get_random_graph(10, 0.2, directed=True)],
              "n=1e2, m=1e2": [get_random_graph(100, 0.02, directed=True)],
              #"n=1e2, m=1.7e2": [get_random_graph(100, 0.017, directed=True)],
              #"n=1e3, m=1.4e3": [get_random_graph(1000, 0.0014, directed=True)],
              "n=1e3, m=1e3": [get_random_graph(1000, 0.002, directed=True)],
              "n=1e3, m=1e5": [get_random_graph(1000, 0.2, directed=True)],
              #"n=1e4, m=1e6": [get_random_graph(10000, 0.02, directed=True)],
              #"n=1e4, m=1e7": [get_random_graph(10000, 0.2, directed=True)],
              #"caveman(100,10)": [connected_caveman_graph(100, 10)],
              #"windmill(10, 10)": [windmill_graph(10, 10)],
              #"nary_tree(3, 1000)": [full_rary_tree(2, 1000)],
              #"complete(20)": [complete_graph(20)],
              }

    benchmarking.run(funcs, params, decimals=2)

if __name__ == '__main__':
    test_dag_speed()
