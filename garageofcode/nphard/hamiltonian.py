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

def get_unsatisfied(tspath): # assumes 0/1 graph
    path = tspath.get_path()
    for u in path + [path[0]]:
        if tspath.D[u, tspath.G[u]]:
            return u
    return None

def rnr_cross(G, tspath):
    #tspath = TSPath(D=D)
    N = len(G)
    tspath.greedy_init()
    score = tspath.get_score()

    for i in range(10000):
        u = get_unsatisfied(tspath)
        if u is None:
            return 

        nodes = set(G[u]) | {u}
        prev_G = {u: tspath.G[u] for u in tspath.G}
        singles = list(tspath.ruin(nodes))
        
        # recreate step
        tspath.recreate(singles)

        tspath.exhaust_crosses()

        new_score = tspath.get_score()
        if new_score <= score:
            score = new_score
        else:
            # reverse changes
            tspath.G = prev_G

        if tspath.get_pathlen() < N:
            print("i:", i)
            print("u:", u)
            print("G:", tspath.G)
            raise RuntimeError("dropped nodes!")
        #for u in range(N):
        #    tspath.recreate(list(tspath.ruin([u])))


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
    rnr_cross(G, tspath)
    rnr_score = tspath.get_score()

    print("Greedy score: {0:.1f}".format(greedy_score))
    print("Cross score: {0:.1f}".format(cross_score))
    print("RnR score: {0:.1f}".format(rnr_score))


if __name__ == '__main__':
    main()