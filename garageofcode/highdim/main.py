import time
from itertools import chain, combinations
from collections import deque

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

import networkx as nx

from garageofcode.mip.convex_hull import in_hull

def powerset(s):
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def ncube_corners(n):
    dims = list(range(n))
    A = np.zeros([2**n, n])
    for i, corner in enumerate(powerset(dims)):
        for j in corner:
            A[i, j] = 1
    return A


def rotation(N, num_pairs, theta):
    A = np.eye(N)
    for _ in range(num_pairs):
        x1, x2 = np.random.choice(N, 2, replace=False)
        #th = np.random.random()*0.4 + 0.8
        th = theta
        A = np.dot(A, subrotation(th, x1, x2, N))
    return A


def subrotation(theta, x1, x2, N):
    A = np.eye(N)
    A[x1, x1] = np.cos(theta)
    A[x1, x2] = -np.sin(theta)
    A[x2, x1] = np.sin(theta)
    A[x2, x2] = np.cos(theta)
    return A

def get_contour(V):
    #return [u for i, u in enumerate(V) 
    #        if not in_hull(u, [v for j, v in enumerate(V) if i != j], verbose=False)]
    U = []
    idxs = []
    for i, u in enumerate(V):
        W = [v for j, v in enumerate(V) if np.linalg.norm(v - u) > 1e-6]
        if not in_hull(u, W, verbose=False):
            U.append(u)
            idxs.append(i)
    return U, idxs

def get_corner_graph(N):
    corners = [tuple(elem) for elem in ncube_corners(N)]

    G = nx.Graph()
    for i, u in enumerate(corners):
        u_l = list(u)
        for i in range(N):
            if u_l[i]:
                u_l[i] = 0
                v = tuple(u_l)
                j = corners.index(v)
                G.add_edge(i, j)
                u_l[i] = 1

    return G


def get_closest_to_xy(P):
    return np.argmin(np.sum(P[2:, :], axis=1))


def get_visible(G, P, contour):
    i = get_closest_to_xy(P)
    P = [tuple(elem) for elem in P.T]
    u = P[i]
    queue = deque([i])
    visible = {i}
    while queue:
        i = queue.popleft()
        for j in G[i]:
            if j not in visible:
                visible.add(j)
                if j not in contour:
                    queue.append(j)
    return visible


def main():
    np.random.seed(0)
    N = 3
    num_iter = 100
    scale = np.sqrt(N) + 0.5
    P = ncube_corners(N).T * 2 - 1
    G = get_corner_graph(N)
    #print(points)
    A0 = rotation(N, 5, 0.5)
    A0 /= np.linalg.det(A0)


    for i in range(num_iter):
        U, contour_idxs = get_contour(P[:2, :].T)
        #print(U)
        U = list(sorted(U, key=lambda x: np.arctan2(x[1], x[0])))
        visible = get_visible(G, P, contour_idxs)
        print(visible)
        #print(U)
        #print()
        polygon = Polygon(U, True)
        p = PatchCollection([polygon])
        fig, ax = plt.subplots()
        ax.add_collection(p)
        ax.set_xlim([-scale, scale])
        ax.set_ylim([-scale, scale])
        ax.axis("off")
        plt.savefig(f"../../../results/highdim/projections/{i:04d}.png")
        plt.close()

        P = np.dot(A0, P)
    

if __name__ == '__main__':
    main()

    #G = get_corner_graph(5)
    #print(len(G.edges))

    # how to plot only visible points?
    # strategy idea:
    # find point closest to x1 = x2 = 0
    # this must be visible
    # so must its neighbours
    # keep branching, except from corners on the contour
