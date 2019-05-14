import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import time
import numpy as np
import matplotlib.pyplot as plt

import torch
from torch import nn
from torch.nn import functional as F
from torch.utils import data as torch_data

from nn.models import MLP

def fit(model, X, Y, learning_rate, batch_size, num_epochs):
    optimizer = torch.optim.SGD(model.parameters(), 
                       lr=learning_rate, 
                       momentum=0.9, 
                       weight_decay=0.01)

    fig, ax_loss = plt.subplots()

    iterations = []
    losses = []
    corrects = []

    trainloader = torch_data.DataLoader(list(zip(*(X, Y))), batch_size=64, shuffle=True)

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

                plt.draw()
                plt.pause(0.05)

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
    sizes = [2] + [20]*2 + [1]
    model = MLP(sizes, activation=nn.ReLU(), out_activation=nn.Sigmoid())

    # fit
    num_epochs = 10000
    learning_rate = 0.005
    batch_size = 50
    fit(model, X, Y, learning_rate, batch_size, num_epochs)

if __name__ == '__main__':
    main()