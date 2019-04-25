import os
import numpy as np
from itertools import product, groupby
from collections import namedtuple
import csv

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

import networkx as nx
from sklearn.manifold import MDS

main_dir = "/home/jdw/garageofcode"
gif_dir = os.path.join(main_dir, "results/tda/gif")

SpectralType = namedtuple("SpectralType", ["metal", "type_short", "type_full"])

def get_mds(X, metric, dim=2):
    mds = MDS(n_components=dim, dissimilarity='precomputed')
    M = [[metric(xi, xj) for xj in X] for xi in X]
    return mds.fit_transform(M), mds  

def load_spectrum(fn):
    wavelength_col = 0
    val_col = 1
    with open(fn, "r") as f:
        reader = csv.reader(f, delimiter=' ')
        next(reader)
        next(reader)
        next(reader)
        wavelengths = []
        vals = []
        for i, line in enumerate(reader):
            if not line:
                continue
            if i % 10 != 0:
                continue
            while '' in line:
                line.remove('')
            #print("line:", line)
            wavelengths.append(float(line[wavelength_col]))
            vals.append(float(line[val_col]))

        #plt.plot(wavelengths, vals)
        #plt.show()
    return np.array(vals)

def load_stars(N):
    data_path = os.path.join(main_dir, "data/stars")

    spectra = {}
    for i, file in enumerate(os.listdir(data_path)):
        if i > N:
            break
        path = os.path.join(data_path, file)
        spectrum = load_spectrum(path)
        if max(spectrum) > 10:
            continue
        name = file[2:-3]
        if name[0] in ["r", "w"]:
            metal = name[0]
            tp = name[1]
            tp_full = name[1:3]
        else:
            metal = "n"
            tp = name[0]
            tp_full = name[0:2]
        spectra[SpectralType(metal, tp, tp_full)] = spectrum

    print("num spectra:", len(spectra))
    return spectra

def read_custom(N):
    data_path = os.path.join(main_dir, "data/test.csv")
    
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

def relative(xi, xj):
    xi = xi / np.sum(xi)
    xj = xj / np.sum(xj)
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

def graph_3d(X):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    metric = relative
    X_transformed, mds = get_mds(X, metric, dim=3)

    print("MDS complete")

    plt.axis('off')

    xcoords, ycoords, zcoords = zip(*X_transformed)    
    ax.scatter(xcoords, ycoords, zcoords)

    plt.show()

def graph_3d_spectra(star2spectrum):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    metric = relative
    S_transformed, mds = get_mds([spectrum for _, spectrum in sorted(star2spectrum.items())], metric, dim=3)
    star2spectrum_t = {star: spectrum_t for star, spectrum_t in zip(sorted(star2spectrum.keys()), S_transformed)}

    plt.axis('off')

    legends = []
    for tp, group in groupby(sorted(star2spectrum), key=lambda star: star.metal):
        legends.append(tp)
        X = [star2spectrum_t[star] for star in group]
        xcoords, ycoords, zcoords = zip(*X)    
        ax.scatter(xcoords, ycoords, zcoords)

    ax.legend(legends)

    plt.show()

def graph_gif(X):
    fig, ax = plt.subplots()

    metric = relative
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
    #X = load_data(N)
    #X = sliding_windows(X, 5)
    name2spectrum = load_stars(131)

    #print(name2spectrum.keys())

    graph_3d_spectra(name2spectrum)

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