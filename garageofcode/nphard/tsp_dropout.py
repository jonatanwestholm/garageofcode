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


def get_path(G):
    i = 0
    path = []
    while True:
        path.append(i)
        i = G[i]
        if not i:
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


def swap(G, u0, u1, u2):
    G[u0], G[u1], G[u2] = G[u2], G[u0], G[u1]
    if get_pathlen(G) < N:
        # in case, orientation was wrong
        # it will only have to recurse once
        swap(G, u0, u1, u2)


def tsp(points):
    global N
    N = len(points)
    # distance matrix
    D = np.array([[np.linalg.norm(x - y) for y in points] for x in points])

    G = {} # directed graph that stores the path
    for i in range(N):
        G[i] = (i+1) % N

    score = get_score(G, D)
    for i in range(100000):
        if i % 2000 == 0:
            print("{0:.1f}".format(score))
        u = np.random.choice(N, size=3, replace=False)
        swap(G, *u)
        new_score = get_score(G, D)
        if new_score <= score:
            score = new_score
        else:
            #if np.random.rand() > 0: #10**((score - new_score) / 10 * np.log(i+1)):
            swap(G, *(reversed(u)))
            
            #else:
            #    score = new_score

    return get_path(G)


def main():
    np.random.seed(0)
    #  problem parameters
    n = 1000
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