import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import numpy as np
import matplotlib.pyplot as plt

from sampling.box_fractal_samples import NBox, generate_boxes, profile_sample, draw_boxes

def white_noise(y, std):
    return y + np.random.normal()*std

def main():
    N = 100000
    #transition = lambda y: white_noise(y, 1)
    #space = {"yt_1": (0, 1), "yt": (0, 1)}
    space = [(-1, 1), (-0.01, 0.01)]
    boxes = generate_boxes(space, 100)
    transition = lambda yt_1: yt_1 + profile_sample([yt_1], boxes)

    y = np.zeros([N])
    yt = 0

    for t in range(N):
        yt = transition(yt)
        if yt < -1 or yt > 1:
            yt = np.random.normal()*0.01
            y[t] = None
        else:
            y[t] = yt

    y_prev, y_post = y[:-1], y[1:]
    y_diff = y_post - y_prev

    fig, ax = plt.subplots(ncols=2)
    ax_series, ax_scatter = ax

    ax_series.plot(y, 'r')
    ax_series.set_xlabel("Iteration")
    ax_series.set_ylabel("Value")
    ax_series.set_title("Series")

    draw_boxes(ax_scatter, boxes)
    ax_scatter.scatter(y_prev, y_diff, s=0.3, c='r')
    ax_scatter.set_xlabel("y(t-1)")
    ax_scatter.set_ylabel("y(t) - y(t-1)")
    ax_scatter.set_title("Transitions")

    plt.show()

if __name__ == '__main__':
    main()