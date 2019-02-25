import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import numpy as np
import random
import matplotlib.pyplot as plt

from sampling.box_sampling import NBox, profile_sample, draw_boxes
from sampling.box_sampling import box_tree_entropy, mutate_box_tree, generate_box_tree
from sampling.box_sampling import get_leafs, num_leafs

def white_noise(y, std):
    return y + np.random.normal()*std

def adversarial_random(T, num_iter):
    N = num_leafs(T)
    save_dir = "/home/jdw/garageofcode/results/sampling/gif"
    fig, (ax_boxes, ax_hist) = plt.subplots(nrows=2)
    best_score = box_tree_entropy(T)
    print("Init score: {0:.3f}".format(best_score))
    for i in range(num_iter):
        T_new = mutate_box_tree(T)
        score = box_tree_entropy(T_new)
        if score < best_score:
            print(i, "New best score: {0:.3f}".format(score))
            T = T_new
            best_score = score
            ax_boxes.clear()
            ax_hist.clear()
            draw_boxes(ax_boxes, get_leafs(T))
            ax_boxes.set_title("Iteration: {0:d}\nEntropy: {1:.3f}".format(i, score))
            ax_boxes.axis("off")
            volumes = [np.log2(box.volume()) for box in get_leafs(T)]
            ax_hist.hist(volumes, bins=range(-50, 1))
            #ax_hist.set_xlim([-3*np.log2(N), 0])
            ax_hist.set_xlabel("log2(box volume)")
            ax_hist.set_ylabel("Occurrences")
            ax_hist.set_title("Histogram box volumes")
            plt.draw()
            plt.pause(0.01)
            path = os.path.join(save_dir, "{0:06d}.png".format(i))
            plt.savefig(path)

def main():
    N = 64
    num_iter = 100000
    #transition = lambda y: white_noise(y, 1)
    #space = {"yt_1": (0, 1), "yt": (0, 1)}
    residual = False
    if residual:
        space = [(-1, 1), (-0.01, 0.01)]        
    else:
        space = [(0, 1), (0, 1)]

    T = generate_box_tree(space, N)
    adversarial_random(T, num_iter)

    return

    if residual:
        transition = lambda yt_1: yt_1 + profile_sample([yt_1], boxes)
    else:
        transition = lambda yt_1: profile_sample([yt_1], boxes)

    y = []
    yt = 0

    for t in range(N):
        yt = transition(yt)
        if yt < -1 or yt > 1:
            break
            yt = np.random.normal()*0.01
            y.append(None)
        else:
            y.append(yt)
    y = np.array(y)

    y_prev, y_post = y[:-1], y[1:]
    y_diff = y_post - y_prev

    fig, ax = plt.subplots(nrows=2)
    ax_series, ax_scatter = ax

    ax_series.plot(y, 'r')
    ax_series.set_xlabel("Iteration")
    ax_series.set_ylabel("Value")
    ax_series.set_title("Series")

    draw_boxes(ax_scatter, boxes)
    if residual:
        ax_scatter.scatter(y_prev, y_diff, s=0.3, c='r')
        ax_scatter.set_ylabel("y(t) - y(t-1)")
    else:
        ax_scatter.scatter(y_prev, y_post, s=0.3, c='r')
        ax_scatter.set_ylabel("y(t)")
    ax_scatter.set_xlabel("y(t-1)")
    #ax_scatter.set_title("Transitions")

    plt.show()

if __name__ == '__main__':
    main()