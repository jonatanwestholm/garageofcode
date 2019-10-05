import numpy as np

import networkx as nx

def get_random_graph(n, rate):
    G = nx.Graph()

    for i in range(n):
        G.add_node(i)

    for i in range(n):
        for j in range(i+1, n):
            if np.random.random() < rate:
                G.add_edge(i, j)

    return G