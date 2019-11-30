import time
from itertools import chain, combinations

import numpy as np
import matplotlib.pyplot as plt

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


def main():
    N = 10
    #points = ncube_corners(N)
    #print(points)
    A = rotation(N, 10, 0.5)
    #print(A)

    plt.imshow(A)
    plt.show()

    

if __name__ == '__main__':
    main()