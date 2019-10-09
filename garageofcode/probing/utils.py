import numpy as np

import networkx as nx

def get_random_graph(n, rate, directed=False):
    if directed:
        G = nx.DiGraph()
    else:
        G = nx.Graph()

    for i in range(n):
        G.add_node(i)

    for i in range(n):
        if directed:
            lb = 0
        else:
            lb = i + 1
        for j in range(lb, n):
            if np.random.random() < rate:
                G.add_edge(i, j)

    return G