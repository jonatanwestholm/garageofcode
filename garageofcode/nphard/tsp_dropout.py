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


def main():
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


if __name__ == '__main__':
    main()