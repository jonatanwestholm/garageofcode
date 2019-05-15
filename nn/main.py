import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import time
import numpy as np
import matplotlib.pyplot as plt

from sklearn.manifold import MDS
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils import data as torch_data

from nn.models import MLP

def get_mds(X, metric, dim=2):
    mds = MDS(n_components=dim, dissimilarity='precomputed')
    M = [[metric(xi, xj) for xj in X] for xi in X]
    return mds.fit_transform(M), mds  

def euclidean(xi, xj):
    xi = np.array(xi)
    xj = np.array(xj)
    return np.linalg.norm(xi - xj)

def plot_mds(ax, X, mds=None):
    ax.cla()
    X_fit, mds = get_mds(X, euclidean)

    X_fit -= X_fit[0, :]
    X_fit /= np.linalg.norm(X_fit[-1, :])
    X_fit /= np.sign(X_fit[-1, :])
    x1, x2 = zip(*X_fit)
    x1 = list(x1)
    x2 = list(x2)

    ax.plot(x1, x2, color='b', alpha=0.2)
    ax.scatter(x1, x2, color='b', alpha=0.2)
    ax.scatter(x1[0], x2[0], color='g')
    ax.scatter(x1[-1], x2[-1], color='r')
    ax.set_title("Parameter convergence")
    ax.legend(["Projection of path", "","Start", "End"])

def fit(model, X, Y, learning_rate, batch_size, num_epochs, loss_fcn=F.mse_loss):
    optimizer = torch.optim.SGD(model.parameters(), 
                       lr=learning_rate,
                       momentum=0.9,
                       weight_decay=0.01)

    fig, (ax_weights, ax_mds, ax_loss) = plt.subplots(ncols=3)

    iterations = []
    losses = []
    corrects = []
    t2params = []

    trainloader = torch_data.DataLoader(list(zip(*(X, Y))), 
                                        batch_size=batch_size, 
                                        shuffle=True)

    i = 0
    for _ in range(num_epochs):
        for i, batch in enumerate(trainloader, i):
            x, y = batch
            y_est = model.forward(x)

            loss = loss_fcn(y_est, y)
            #correct = (y_est-0.5) * (y-0.5) > 0
            #correct = correct.float()
            #correct = torch.mean(correct)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if i % 97 == 0:
                iterations.append(i)
                losses.append(np.sqrt(loss.item()))
                #corrects.append(correct.item())

                ax_loss.semilogy(iterations, losses, 'b')
                #ax_loss.plot(iterations, corrects, 'g')
                ax_loss.set_title("Loss")
                ax_loss.set_ylabel("RMS")
                ax_loss.set_xlabel("Iteration")

                #ax_loss.legend(["Cross entropy loss", "Rate correct"])

                params = []
                for param in model.parameters():
                    for elem in param.data.view(-1, 1):
                        params.extend(elem.numpy())
                t2params.append(params)
                if len(t2params) > 2 and len(t2params) % 10 == 0:
                    plot_mds(ax_mds, t2params[-50:])
                    #plot_mds(ax_mds, t2params)

                #all_weights = np.array(t2params)
                #ax_weights.plot(all_weights)
                plot_fit(ax_weights, model, X, Y)

                plt.draw()
                plt.pause(0.05)
    plt.show()

def plot_fit(ax, model, X, Y):
    ax.cla()

    with torch.no_grad():
        Y_est = model.forward(X)

    y = Y.numpy()
    y_est = Y_est.numpy()

    errs = np.linalg.norm(y-y_est, axis=1)
    y_est_norm = np.linalg.norm(y_est, axis=1)
    y_est_norm = np.ravel(y_est_norm)

    ax.scatter(y_est_norm, errs, color='b', alpha=0.1)
    ax.set_yscale('log')

    ax.set_title("Fit")
    ax.set_xlabel("|Y_est|")
    ax.set_ylabel("|Y_est - Y|")

def tutorial():
    # ground truth
    f = lambda x: x[0]**2 + x[1]**2 <= 1

    # data
    N = 10000
    scale = 2.4
    X = scale*torch.rand(N, 2) - scale/2
    Y = torch.from_numpy(np.array([f(x) for x in X]))
    Y = Y.float()

    # model
    sizes = [2] + [5]*2 + [1]
    model = MLP(sizes, activation=nn.ReLU(), out_activation=nn.Sigmoid())

    # fit
    num_epochs = 500
    learning_rate = 0.001
    batch_size = 64
    fit(model, X, Y, learning_rate, batch_size, num_epochs)

def linsys(X, n):
    A = X[:n**2].view(n, n).numpy()
    b = X[n**2:].view(n, 1).numpy()
    return np.linalg.lstsq(A, b)[0]

def main():
    # ground truth
    f = linsys

    # data
    N = 10000
    n = 3
    num_output = n
    num_input = n*num_output + num_output
    scale = 1
    X = scale*torch.rand(N, num_input) + scale/2
    Y = torch.from_numpy(np.array([f(x, n) for x in X]))
    Y = Y.float()

    #print(Y.shape)
    mask = np.linalg.norm(Y, axis=1) < 10
    mask = np.ravel(mask)
    mask = torch.from_numpy(mask)
    #print(mask.shape)
    X = torch.squeeze(X[mask, :])
    Y = torch.squeeze(Y[mask, :])
    #print(Y.shape)
    #print(X)
    #exit(0)


    # model
    sizes = [num_input] + [60]*3 + [num_output]
    model = MLP(sizes, activation=nn.Tanh())

    # fit
    num_epochs = 5000
    learning_rate = 0.0005
    batch_size = 64
    fit(model, X, Y, learning_rate, batch_size, num_epochs)

if __name__ == '__main__':
    main()