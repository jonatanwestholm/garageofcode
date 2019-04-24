import os
import numpy as np
from itertools import product

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

import networkx as nx
from sklearn.manifold import MDS

gif_dir = "/home/jdw/garageofcode/results/tda/gif"

def get_mds(X, metric):
    mds = MDS(n_components=2, dissimilarity='precomputed')
    M = [[metric(xi, xj) for xj in X] for xi in X]
    return mds.fit_transform(M), mds    

def recurrent_data(N):
    Y = [0]
    for _ in range(N):
        y = -0.9*Y[-1] + np.random.normal()*0.1
        Y.append(y)

    X = []
    for i in range(N):
        X.append((Y[i], Y[i+1]))

    return X

def periodic_data(N):
    Y = [0]
    for i in range(N):
        y = np.sin(i / 11.1 * 2*np.pi) + np.random.normal()*0.1
        #y += np.sin(i / 17.1 * 2*np.pi)
        Y.append(y)

    X = []
    dim = 5
    for i in range(N-dim+2):
        X.append(Y[i:i+dim])

    return X

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

    X_transformed, mds = get_mds(X, metric)

    M = [(metric(xi, xj), xi_t, xj_t) for i, (xi, xi_t) in enumerate(zip(X, X_transformed)) 
                                  for xj, xj_t in zip(X[i+1:], X_transformed[i+1:])]

    plt.axis('off')

    xcoords, ycoords = zip(*X_transformed)    
    ax.scatter(xcoords, ycoords)

    img_number = 0
    for d, xi_t, xj_t in sorted(M):
        xi1, xi2 = xi_t
        xj1, xj2 = xj_t
        ax.plot([xi1, xj1], [xi2, xj2], color='b')

        ax.set_title("d={0:.3f}".format(d))

        plt.draw()
        plt.pause(0.01)

        path = os.path.join(gif_dir, "{:03d}".format(img_number))
        plt.savefig(path)
        img_number += 1

    plt.show()

def main():
    N = 100
    #X = [tuple(np.random.random([2])) for _ in range(N)]
    #X = recurrent_data(N)
    X = periodic_data(N)

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