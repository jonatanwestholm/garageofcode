from collections import Counter
from functools import partial
from itertools import chain

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

from garageofcode.mip.tsp import tsp

def get_data(n, r):
    """Return n points in [[0, r), [0, r)]
    """

    return np.random.random([n, 2]) * r

def flatten(s):
    return [elem for sublist in s for elem in sublist]

def main():
    #  how to join solutions afterwards? 
    #  -take out most commonly used edges, just throw them together?
    #  need not run so far, just check if popular edges 
    #    overlap with exact edges
    #  and if they are more robust to pertubations of the problem
    #  how can we qualify pertubations of the problem?

    np.random.seed(0)
    #  problem parameters
    n = 7
    k = 4
    r = 100

    #  solution parameters
    num_iter = 20

    points = [(i, p) for i, p in enumerate(get_data(n, r))]
    if 1:
        path = tsp(points)
        path_coords = [points[id_num[0]][1] for id_num in path]
        x_coords, y_coords = zip(*path_coords)
        plt.scatter(x_coords, y_coords, s=10, color='r')
        plt.plot(x_coords, y_coords)
        plt.show()


    '''
    sample = partial(np.random.choice, size=k, replace=False)
    c = Counter(chain.from_iterable(tsp([points[i] 
                            for i in sample(n)]) for _ in range(num_iter)))


    for (u, v), num in c.items():
        u = points[u][1]
        v = points[v][1]
        x, y = zip(*[u, v])
        plt.plot(x, y, linewidth=num, color='b')
    plt.show()
    '''

    '''
    #  solution synthesis
    #  this is super stupid
    G = nx.Graph()
    for i in range(n):
        G.add_node(i)
    def unsaturated(u):
        return len(G[u]) <= 1
    for (u, v), _ in c.most_common():
        if unsaturated(u) and unsaturated(v):
            try:
                nx.shortest_path_length(G, u, v)
            except nx.exception.NetworkXNoPath:
                G.add_edge(u, v)

    for u, v in G.edges():
        u = points[u][1]
        v = points[v][1]
        x, y = zip(*[u, v])
        plt.plot(x, y, color='b')
    plt.show()
    '''


if __name__ == '__main__':
    main()