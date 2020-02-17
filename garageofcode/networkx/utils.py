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
        for j in range(i+1, n):
            if np.random.random() < rate:
                if directed:
                    if np.random.random() < 0.5:
                        G.add_edge(i, j)
                    else:
                        G.add_edge(j, i)
                else:
                    G.add_edge(i, j)
    return G