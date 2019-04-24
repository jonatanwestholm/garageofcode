import os
import numpy as np
from itertools import product
import csv

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

import networkx as nx
from sklearn.manifold import MDS

gif_dir = "/home/jdw/garageofcode/results/tda/gif"

def get_mds(X, metric):
    mds = MDS(n_components=2, dissimilarity='precomputed')
    M = [[metric(xi, xj) for xj in X] for xi in X]
    return mds.fit_transform(M), mds    

def read_custom(N):
    data_path = "/home/jdw/garageofcode/data/test.csv"
    
    i = 0
    with open(data_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for line in reader:
            yield float(line[1])
            i += 1
            if i >= N:
                break

def load_data(N):
    return list(read_custom(N))

def sliding_windows(Y, dim):
    X = []
    for i in range(len(Y)-dim+1):
        X.append(Y[i:i+dim])

    return X    

def random_data(N):
    Y = [0]
    for _ in range(N):
        y = np.random.normal()*0.1
        Y.append(y)

    return Y[1:]

def recurrent_data(N):
    Y = [0]
    for _ in range(N):
        y = 0.9*Y[-1] + np.random.normal()*0.1
        Y.append(y)

    return Y[1:]

def periodic_data(N):
    Y = [0]
    for i in range(N):
        y = np.sin(i / 11.1 * 2*np.pi) + np.random.normal()*0.1
        #y += np.sin(i / 17.1 * 2*np.pi)
        Y.append(y)

    return Y[1:]

def euclidean(xi, xj):
    xi = np.array(xi)
    xj = np.array(xj)
    return np.linalg.norm(xi - xj)

def corr(xi, xj):
    xi = np.array(xi)
    xj = np.array(xj)
    xi -= np.mean(xi)
    xj -= np.mean(xj)
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

    metric = corr
    X_transformed, mds = get_mds(X, metric)

    print("MDS complete")

    M = [(metric(xi, xj), xi_t, xj_t) for i, (xi, xi_t) in enumerate(zip(X, X_transformed)) 
                                  for xj, xj_t in zip(X[i+1:], X_transformed[i+1:])]

    plt.axis('off')

    xcoords, ycoords = zip(*X_transformed)    
    ax.scatter(xcoords, ycoords)

    img_number = 0
    for d, xi_t, xj_t in sorted(M, key=lambda x: x[0]):
        xi1, xi2 = xi_t
        xj1, xj2 = xj_t
        ax.plot([xi1, xj1], [xi2, xj2], color='b')

        ax.set_title("d={0:.3f}".format(d))

        plt.draw()
        plt.pause(0.01)

        path = os.path.join(gif_dir, "{:03d}".format(img_number))
        plt.savefig(path)
        img_number += 1
        break

    plt.show()

def main():
    N = 300
    #X = [tuple(np.random.random([20])) for _ in range(N)]
    #X = random_data(N)
    #X = recurrent_data(N)
    #X = periodic_data(N)
    X = load_data(N)
    X = sliding_windows(X, 5)

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