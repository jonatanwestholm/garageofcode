import time
import random
from collections import Counter
from functools import partial
from itertools import chain

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

from garageofcode.mip.tsp import tsp as tsp_mip

class TSPath:
    def __init__(self, points=None, G=None):
        """Should I restrict this to having input either
        points or G? What are the use cases of having both?
        Spinning off sub-optimizations with an init path?
        YAGNI, probably
        It's just so ugly now
        """
        if points is not None:
            self.N = len(points)
            self.points = points
            #  distance matrix
            self.D = np.array([[np.linalg.norm(x - y) 
                            for y in points] for x in points])
        if G is None:
            self.G = {}  # single linked list
            for i in range(self.N):
                self.G[i] = (i+1) % self.N
            self.cycle_nodes = set(range(self.N))
        else:
            self.N = len(G)
            self.G = G
            self.cycle_nodes = set(G)
        self.in_cycle = self.N

    def greedy_init(self):
        node = next(iter(self.G))
        path = [node]
        remaining = set(self.G) - {node}
        while remaining:
            nearest = min(remaining, key=lambda j: self.D[node][j])
            path.append(nearest)
            remaining.remove(nearest)
            node = nearest
        for i, j in zip(path, path[1:] + [path[0]]):
            self.G[i] = j

    def get_path(self, i0=0):
        i = i0
        path = []
        while True:
            path.append(i)
            i = self.G[i]
            if i == i0:
                return path

    def get_pathlen(self, i0=0):
        i = i0
        pathlen = 0
        while True:
            pathlen += 1
            i = self.G[i]
            if i == i0:
                return pathlen

    def get_score(self, i0=0):
        score = 0
        path = self.get_path(i0)
        for i, j in zip(path, path[1:] + [path[0]]):
            score += self.D[i, j]
        return score

    def reverse_cycle(self, u0):
        path = self.get_path(u0)
        for i, j in zip(path, [path[-1]] + path[:-1]):
            self.G[i] = j
        if len(path) > 1:
            return path[1]
        else:
            return path[0]

    def triple_swap(self, u0, u1, u2):
        G = self.G
        G[u0], G[u1], G[u2] = G[u2], G[u0], G[u1]
        if self.get_pathlen() < self.in_cycle:
            # in case orientation was wrong
            # it will only have to recurse once
            self.triple_swap(u0, u1, u2)

    def cross_swap(self, u0, u1):
        G = self.G
        G[u0], G[u1] = G[u1], G[u0]
        u0 = self.reverse_cycle(u0)
        #print("u0:", u0)
        G[u0], G[u1] = G[u1], G[u0]  # ha-ha!
        if self.get_pathlen() < self.in_cycle:
            raise RuntimeError("dropped nodes!")

    def improving_cross(self, u0, u1):
        G = self.G
        D = self.D
        v0, v1 = G[u0], G[u1]
        return D[u0, u1] + D[v0, v1] < D[u0, v0] + D[u1, v1]

    def remove_head(self, u):
        """
        Removes the head of u from the path
        Returns the removed node
        """
        G = self.G
        v = G[u]
        if u == v:
            # u is already single
            # don't decrement in_cycle
            return u
        G[u], G[v] = G[v], G[u]
        self.in_cycle -= 1
        self.cycle_nodes.remove(v)
        return v

    def insert(self, u, v):
        """
        Inserts v at the head of u
        Assumes that G[v] = v
        """
        G = self.G
        if u == v:
            # don't increment in_cycle
            return
        G[u], G[v] = G[v], G[u]
        self.in_cycle += 1
        self.cycle_nodes.add(v)

    def detour(self, u0, u1, v):
        """
        What is the cost difference of 
        doing a detour through v when 
        going from u0 to u1?
        """
        D = self.D
        return D[u0, v] + D[v, u1] - D[u0, u1]

    def optimal_insert(self, v):
        """
        Which u gives the lowest cost increase
        with self.insert(u, v)?
        """
        return min(self.cycle_nodes, key=lambda u: self.detour(u, self.G[u], v))

    def ruin(self, nodes):
        """
        Remove the heads of `nodes`
        Return the removed nodes
        """
        # should be a set in case v = G[u], for some u, v both in nodes
        return set([self.remove_head(u) for u in nodes])

    def recreate(self, nodes):
        """
        Simple, incremental recreate step
        """
        random.shuffle(nodes)
        for v in nodes:
            self.insert(self.optimal_insert(v), v)



def get_data(n, r):
    """Return n points in [[0, r), [0, r)]
    """
    return np.random.random([n, 2]) * r


def test_cross_swap():
    G = {}
    G[0] = 1
    G[1] = 2
    G[2] = 3
    G[3] = 0
    tspath = TSPath(G=G)
    print("G0:", tspath.G)

    tspath.cross_swap(0, 2)
    print("G1:", tspath.G)

def tsp_local(points):
    """
    Random greedy search with local operations
    """
    N = len(points)
    tspath = TSPath(points)
    tspath.greedy_init()

    score = tspath.get_score()
    for i in range(10001):
        if i % 1000 == 0:
            print("{0:.1f}".format(score))
        r = np.random.rand()
        if r < 0.33:
            u = np.random.choice(N, size=2, replace=False)
            if tspath.improving_cross(*u):
                tspath.cross_swap(*u)
        elif r < 0.67:
            u = np.random.choice(N, size=3, replace=False)
            tspath.triple_swap(*u)
            new_score = tspath.get_score()
            if new_score <= score:
                score = new_score
            else:
                # metropolis-hastings
                #if np.random.rand() > 0: #10**((score - new_score) / 10 * np.log(i+1)):
                tspath.triple_swap(*(reversed(u)))
        else:
            R = 50  # radius for ruin

            # ruin step
            u = np.random.randint(N)
            r = np.random.random() * R
            nodes = filter(lambda v: tspath.D[v, u] < r, tspath.G)
            prev_G = {u: tspath.G[u] for u in tspath.G}
            singles = list(tspath.ruin(nodes))
            
            # recreate step
            tspath.recreate(singles)

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

    return tspath.get_path()


def tsp_ruin_recreate(points):
    R = 20  # radius for ruin

    N = len(points)
    tspath = TSPath(points)
    tspath.greedy_init()

    score = tspath.get_score()
    for i in range(10000):
        if i % 1000 == 0:
            print("{0:.1f}".format(score))
        
        # ruin step
        u = np.random.randint(N)
        r = np.random.random() * R
        nodes = filter(lambda v: tspath.D[v, u] < r, tspath.G)
        prev_G = {u: tspath.G[u] for u in tspath.G}
        singles = tspath.ruin(nodes)
        
        # recreate step
        tspath.recreate(singles)

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

    return tspath.get_path()


def main():
    np.random.seed(0)
    #  problem parameters
    n = 1000
    k = 4
    r = 100

    #  solution parameters
    num_iter = 20
    #tsp = tsp_ruin_recreate
    tsp = tsp_local

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