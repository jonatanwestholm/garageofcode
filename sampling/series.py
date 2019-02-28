import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import time
import numpy as np
from copy import copy
from scipy.stats import entropy
from collections import defaultdict
import matplotlib.pyplot as plt

from sampling.box_sampling import SamplingBoxTree, draw_boxes

def white_noise(y, std):
    return y + np.random.normal()*std

def adversarial_random(T, num_iter):
    N = num_leafs(T)
    save_dir = "/home/jdw/garageofcode/results/sampling/gif"
    fig, (ax_series, ax_boxes, ax_hist) = plt.subplots(nrows=3)
    #best_score, _ = series_entropy(T)
    best_score = -100
    #print("Init score: {0:.3f}".format(best_score))
    for i in range(num_iter):
        T_new = T.copy()
        T_new = T_new.mutate_box_tree()
        score_box = T_new.entropy()
        #score_box = 0
        _, _, y = series_entropy(T_new)
        score_series, dist = series_entropy_markov(T_new)
        score = score_series - score_box
        #print(score)
        if score >= best_score - 0.01:
            T = T_new
            if score >= best_score:
                print(i, "New best score: {0:.3f}".format(score))
                best_score = score
            ax_series.clear()
            ax_boxes.clear()
            ax_hist.clear()
            ax_series.plot(y, 'r')
            ax_series.set_title("Iteration: {0:d}\nEntropy: {1:.3f}".format(i, score))
            y_prev, y_post = y[:-1], y[1:]
            draw_boxes(ax_boxes, get_leafs(T))
            ax_boxes.scatter(y_prev, y_post, s=0.3, c='r')
            ax_boxes.set_ylabel("y(t)")
            ax_boxes.set_xlabel("y(t-1)")
            #ax_boxes.axis("off")
            #volumes = [np.log2(box.volume()) for box in get_leafs(T)]
            #ax_hist.hist(volumes, bins=range(-50, 1))
            #ax_hist.set_xlim([-3*np.log2(N), 0])
            #counts = [np.log2(counts) for counts in box2count.values()]
            #ax_hist.hist(counts)
            #ax_hist.set_xlim([0, 12])
            ax_hist.hist(np.log2(dist))
            #ax_hist.set_xlim([-12, 0])
            ax_hist.set_xlabel("log2(stationary probability)")
            ax_hist.set_ylabel("Occurrences")
            #ax_hist.set_title("Histogram box volumes")
            plt.draw()
            plt.pause(0.01)
            path = os.path.join(save_dir, "{0:06d}.png".format(i))
            plt.savefig(path)

def series_entropy(T):
    box2count = defaultdict(int)
    y = []
    yt = 0
    for t in range(1024):
        yt, box = T.profile_sample([yt], return_box=True)
        box2count[box] += 1
        if yt < -1 or yt > 1:
            yt = np.random.normal()*0.01
        y.append(yt)
    #print(max(box2count.values()))
    return entropy(box2count.values()), box2count, y

def series_entropy_markov(T):
    stat_dist = T.stationary_distribution()
    #print(stat_dist)
    return entropy(stat_dist), stat_dist

def main():
    #np.random.seed(0)
    #random.seed(0)
    N = 64
    num_iter = 10000
    #transition = lambda y: white_noise(y, 1)
    #space = {"yt_1": (0, 1), "yt": (0, 1)}
    residual = False
    if residual:
        space = [(-1, 1), (-0.01, 0.01)]        
    else:
        space = [(0, 1), (0, 1)]

    T = SamplingBoxTree(space, N)
    boxes = get_leafs(T)

    if residual:
        transition = lambda yt_1: yt_1 + profile_sample([yt_1], T)
    else:
        transition = lambda yt_1: profile_sample([yt_1], T)

    adversarial_random(T, num_iter)

    return

    y = []
    yt = 0

    t0 = time.time()
    for t in range(num_iter):
        yt = transition(yt)
        if yt < -1 or yt > 1:
            break
            yt = np.random.normal()*0.01
            y.append(None)
        else:
            y.append(yt)
        t1 = time.time()
        #print("Time: {0:.3f}".format(t1 - t0))
    y = np.array(y)

    y_prev, y_post = y[:-1], y[1:]
    y_diff = y_post - y_prev

    fig, ax = plt.subplots(nrows=2)
    ax_series, ax_scatter = ax

    ax_series.plot(y, 'r')
    ax_series.set_xlabel("Iteration")
    ax_series.set_ylabel("Value")
    ax_series.set_title("Series")

    draw_boxes(ax_scatter, T)
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