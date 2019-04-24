import os
import numpy as np
from itertools import product

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

import networkx as nx

gif_dir = "/home/jdw/garageofcode/results/tda/gif"

def metric(xi, xj):
    xi = np.array(xi)
    xj = np.array(xj)
    return np.linalg.norm(xi - xj)

def draw_graph(G):
    fig, ax = plt.subplots()

    xcoords, ycoords = zip(*G.nodes())

    ax.scatter(xcoords, ycoords)

    for xi, xj in product(G.nodes(), repeat=2):
        if xj in G[xi]:
            xi1, xi2 = xi
            xj1, xj2 = xj
            ax.plot([xi1, xj1], [xi2, xj2], color='b')

    plt.show()

def graph_gif(X):
    fig, ax = plt.subplots()

    M = [(metric(xi, xj), xi, xj) for i, xi in enumerate(X) for xj in X[i+1:]]

    plt.axis('off')

    xcoords, ycoords = zip(*X)    
    ax.scatter(xcoords, ycoords)

    img_number = 0
    for d, xi, xj in sorted(M):
        xi1, xi2 = xi
        xj1, xj2 = xj
        ax.plot([xi1, xj1], [xi2, xj2], color='b')

        ax.set_title("d={0:.3f}".format(d))

        plt.draw()
        plt.pause(0.01)

        path = os.path.join(gif_dir, "{:03d}".format(img_number))
        plt.savefig(path)
        img_number += 1

    plt.show()

def main():
    N = 20
    X = [tuple(np.random.random([2])) for _ in range(N)]

    graph_gif(X)

    '''
    d = 0.2

    G = nx.Graph()
    for i, xi in enumerate(X):
        G.add_node(xi)
        for xj in X[i+1:]:
            if metric(xi, xj) < d:
                G.add_edge(xi, xj)

    draw_graph(G)
    '''

if __name__ == '__main__':
    main()