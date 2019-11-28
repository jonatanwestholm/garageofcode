import numpy as np

import networkx as nx

from garageofcode.nphard.tsp import TSPath

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


def rnr_cross(D):
    tspath = TSPath(D=D)
    tspath.greedy_init()

    for i in range(1000):
        pass


def main():
    N = 100
    rate = 0.1

    G = get_random_graph(N, rate)
    D = np.zeros([N, N])
    for i in range(N):
        for j in range(i):
            if j in G[i]:
                D[i, j] = 0
            else:
                D[i, j] = 1
    D = D + D.T

    tspath = TSPath(D=D)
    tspath.greedy_init()
    greedy_score = tspath.get_score()
    tspath.exhaust_crosses()
    cross_score = tspath.get_score()

    print("Greedy score: {0:.1f}".format(greedy_score))
    print("Cross score: {0:.1f}".format(cross_score))


if __name__ == '__main__':
    main()