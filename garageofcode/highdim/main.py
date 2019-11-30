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
    return [u for u in V if in_hull(u, V, verbose=False)]

def main():
    N = 2
    num_iter = 10
    P = ncube_corners(N).T * 2 - 1 
    #print(points)
    A0 = rotation(N, 1, np.pi/7)
    A0 /= np.linalg.det(A0)


    for i in range(num_iter):
        U = get_contour(P[:2, :].T)
        print(U)
        U = list(sorted(U, key=lambda x: np.arctan2(x[1], x[0])))
        print(U)
        print()
        polygon = Polygon(U, True)
        p = PatchCollection([polygon])
        fig, ax = plt.subplots()
        ax.add_collection(p)
        ax.set_xlim([-1.5, 1.5])
        ax.set_ylim([-1.5, 1.5])
        plt.savefig("../../../results/highdim/projections/{}.png".format(i))
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