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

def fit(model, X, Y, learning_rate, batch_size, num_epochs):
    optimizer = torch.optim.SGD(model.parameters(), 
                       lr=learning_rate,
                       momentum=0.9,
                       weight_decay=0.01)

    fig, (ax_mds, ax_loss) = plt.subplots(ncols=2)

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

            loss = F.binary_cross_entropy(y_est, y)
            correct = (y_est-0.5) * (y-0.5) > 0
            correct = correct.float()
            correct = torch.mean(correct)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if i % 97 == 0:
                iterations.append(i)
                losses.append(loss.item())
                corrects.append(correct.item())

                ax_loss.plot(iterations, losses, 'b')
                ax_loss.plot(iterations, corrects, 'g')
                ax_loss.set_title("Loss")
                ax_loss.set_ylabel("Binary cross entropy")
                ax_loss.set_xlabel("Iteration")

                ax_loss.legend(["Cross entropy loss", "Rate correct"])

                params = []
                for param in model.parameters():
                    for elem in param.data.view(-1, 1):
                        params.extend(elem.numpy())
                t2params.append(params)
                if len(t2params) > 2 and len(t2params) % 10 == 0:
                    plot_mds(ax_mds, t2params[-50:])
                    #plot_mds(ax_mds, t2params)

                plt.draw()
                plt.pause(0.05)
    plt.show()

def main():
    # ground truth
    f = lambda x: x[0]**2 + x[1]**2 <= 1

    # data
    N = 10000
    scale = 2.4
    X = scale*torch.rand(N, 2) - scale/2
    Y = torch.from_numpy(np.array([f(x) for x in X]))
    Y = Y.float()

    # model
    sizes = [2] + [30]*1 + [1]
    model = MLP(sizes, activation=nn.ReLU(), out_activation=nn.Sigmoid())

    # fit
    num_epochs = 500
    learning_rate = 0.001
    batch_size = 64
    fit(model, X, Y, learning_rate, batch_size, num_epochs)

if __name__ == '__main__':
    main()