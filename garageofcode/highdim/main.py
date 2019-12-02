import time
from itertools import chain, combinations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

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
    for i, u in enumerate(V):
        W = [v for j, v in enumerate(V) if np.linalg.norm(v - u) > 1e-6]
        if not in_hull(u, W, verbose=False):
            U.append(u)
    return U


def main():
    np.random.seed(0)
    N = 5
    num_iter = 200
    scale = np.sqrt(N) + 0.5
    P = ncube_corners(N).T * 2 - 1 
    #print(points)
    A0 = rotation(N, 10, 0.05)
    A0 /= np.linalg.det(A0)


    for i in range(num_iter):
        U = get_contour(P[:2, :].T)
        #print(U)
        U = list(sorted(U, key=lambda x: np.arctan2(x[1], x[0])))
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


    """
    print(np.linalg.det(A0))
    A = np.eye(N)
    #print(A)
    for i in range(10):
        plt.imshow(A)
        plt.title(i)
        #if i % 10 == 0:
        try:
            plt.show()
        except KeyboardInterrupt:
            break
        '''
        else:
            plt.draw()
            plt.pause(0.1)
            plt.close()
        '''
        A = np.dot(A0, A)
    """

    

if __name__ == '__main__':
    main()