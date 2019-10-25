import time
from collections import Counter
from functools import partial
from itertools import chain

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

from garageofcode.mip.tsp import tsp as tsp_mip

def get_data(n, r):
    """Return n points in [[0, r), [0, r)]
    """

    return np.random.random([n, 2]) * r


def get_path(G, i0=0):
    i = i0
    path = []
    while True:
        path.append(i)
        i = G[i]
        if i == i0:
            return path


def get_pathlen(G):
    i = 0
    pathlen = 0
    while True:
        pathlen += 1
        i = G[i]
        if not i:
            return pathlen


def get_score(G, D):
    score = 0
    path = get_path(G)
    for i, j in zip(path, path[1:] + [path[0]]):
        score += D[i, j]
    return score

def reverse_cycle(G, u0):
    path = get_path(G, u0)
    for i, j in zip(path, [path[-1]] + path[:-1]):
        G[i] = j
    if len(path) > 1:
        return path[1]
    else:
        return path[0]

def triple_swap(G, u0, u1, u2):
    G[u0], G[u1], G[u2] = G[u2], G[u0], G[u1]
    if get_pathlen(G) < len(G):
        # in case orientation was wrong
        # it will only have to recurse once
        triple_swap(G, u0, u1, u2)

def cross_swap(G, u0, u1):
    G[u0], G[u1] = G[u1], G[u0]
    u0 = reverse_cycle(G, u0)
    #print("u0:", u0)
    G[u0], G[u1] = G[u1], G[u0]  # ha-ha!
    if get_pathlen(G) < len(G):
        print("dropped!")

def improving_cross(G, D, u0, u1):
    v0, v1 = G[u0], G[u1]
    return D[u0, u1] + D[v0, v1] < D[u0, v0] + D[u1, v1]

def test_cross_swap():
    G = {}
    G[0] = 1
    G[1] = 2
    G[2] = 3
    G[3] = 0
    print("G0:", G)

    cross_swap(G, 0, 2)
    print("G1:", G)

def greedy_init(G, D):
    node = next(iter(G))
    path = [node]
    remaining = set(G) - {node}
    while remaining:
        nearest = min(remaining, key=lambda j: D[node][j])
        path.append(nearest)
        remaining.remove(nearest)
        node = nearest
    return path


def tsp(points):
    N = len(points)
    # distance matrix
    D = np.array([[np.linalg.norm(x - y) for y in points] for x in points])

    G = {} # directed graph that stores the path
    for i in range(N):
        G[i] = (i+1) % N
    path = greedy_init(G, D)
    for i, j in zip(path, path[1:] + [path[0]]):
        G[i] = j

    score = get_score(G, D)
    for i in range(1000000):
        if i % 20000 == 0:
            print("{0:.1f}".format(score))
        r = np.random.rand() < 0.5
        if r:
            u = np.random.choice(N, size=2, replace=False)
            if improving_cross(G, D, *u):
                cross_swap(G, *u)
        else:
            u = np.random.choice(N, size=3, replace=False)
            triple_swap(G, *u)
            new_score = get_score(G, D)
            if new_score <= score:
                score = new_score
            else:
                #if np.random.rand() > 0: #10**((score - new_score) / 10 * np.log(i+1)):
                triple_swap(G, *(reversed(u)))
            
            #else:
            #    score = new_score

    return get_path(G)


def main():
    np.random.seed(0)
    #  problem parameters
    n = 100
    k = 4
    r = 100

    #  solution parameters
    num_iter = 20

    points = get_data(n, r)
    t0 = time.time()
    path = tsp(points)
    t1 = time.time()
    print("time: {0:.3f}".format(t1 - t0))
    path_coords = [points[id_num] for id_num in path]
    x_coords, y_coords = zip(*path_coords)
    plt.scatter(x_coords, y_coords, s=10, color='r')
    plt.plot(x_coords, y_coords)
    plt.show()


if __name__ == '__main__':
    main()

    #test_cross_swap()