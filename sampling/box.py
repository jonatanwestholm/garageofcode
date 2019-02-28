import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import time
from copy import copy
import numpy as np
from itertools import product
from scipy.linalg import null_space
from scipy.stats import entropy
import networkx as nx

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from common.box import Box, BoxTree

class SamplingBox(Box):
    def split(self):
        dim = np.random.choice(list(self.keys()))

        i, j = self[dim]
        mid = (i + j) / 2

        bounds0 = copy(self)
        bounds1 = copy(self)

        bounds0[dim] = (i, mid)
        bounds1[dim] = (mid, j)

        return bounds0, bounds1

    def sample_point(self):
        i, j = zip(*[(i, j) for d, (i, j) in sorted(self.items())])
        i = np.array(i)
        j = np.array(j)
        return i + (j - i) * np.random.random([len(self)])

class SamplingBoxTree(BoxTree):
    def initialize(self, dim2ij, num_leafs):
        self.add_node(SamplingBox(dim2ij))
        self.generate(num_leafs-1)

    def generate(self, num_leafs):
        leafs = self.get_leafs()
        for _ in range(num_leafs):
            box = leafs[np.random.choice(len(leafs))]
            leafs.remove(box)
            ch0, ch1 = box.split()
            self.add_edge(box, ch0)
            self.add_edge(box, ch1)
            leafs.append(ch0)
            leafs.append(ch1)

    def entropy(self):
        return entropy([box.volume() for box in self.get_leafs()])

    def row_transition(self, from_state, to_states):
        row = np.zeros(len(to_states))
        mid = (from_state[0] + from_state[1]) / 2
        dim2val = {0: mid}
        boxes = list(self.profile(dim2val))
        get_end = lambda box: box[0][1]
        for box in sorted(boxes, key=get_end):
            c0 = box.profile(dim2val)
            c0 = c0[1]
            intensity = 1/(c0[1] - c0[0])/len(boxes)
            for idx, c1 in enumerate(to_states):
                intersect = Box.intersection1d(c0, c1)
                if intersect:
                    (i, j) = intersect
                    row[idx] += (j - i) * intensity
        return row

    def markov_transition(self):
        boxes = self.get_leafs()
        get_start = lambda box: box[0][0]
        get_end = lambda box: box[0][1]
        bins = [get_end(box) for box in boxes]
        bins = [min(map(get_start, boxes))] + bins
        bins = list(sorted(set(bins)))
        bins = [(b0, b1) for b0, b1 in zip(bins[:-1], bins[1:])]
        P = [self.row_transition(b, bins) for b in bins]
        return np.array(P)

    def stationary_distribution(self):
        """
        Finds the stationary distribution of the 
        implicit markov chain defined by
        conditional sampling on the box tree, i.e.

        y(t) | y(t-1) ~ T.profile_sample(dim2val={0: y(t-1)})
        """
        P = self.markov_transition()
        N = len(P)
        I = np.identity(N)
        A = P.T - I # get right-kernel
        pi = null_space(A)
        pi = pi / sum(pi)
        pi = [float(item) for item in pi]
        return pi

    def mutate(self):
        """
        Cuts off random subtree
        Adds new leafs, keeping number of leafs the same
        """
        num_leafs_before = self.num_leafs()
        non_leafs = [v for v, d in self.out_degree() if d > 0]
        box = non_leafs[np.random.choice(len(non_leafs))]
        children = list(self[box])
        for child in children:
            self.remove_subtree(child)
        num_leafs_after = self.num_leafs()
        num_removed = num_leafs_before - num_leafs_after
        self.generate(num_removed)

    def profile_sample(self, dim2val, return_box=False):
        if not isinstance(dim2val, dict):
            # if dim2val not dict, assume dim=idx
            dim2val = {dim: val for dim, val in enumerate(dim2val)}
        boxes = list(self.profile(dim2val))
        box = boxes[np.random.choice(len(boxes))]
        projected = box.profile(dim2val)
        projected = SamplingBox(projected)
        point = projected.sample_point()
        if return_box:
            return point, box
        else:
            return point

def generate_boxes(b0, N):
    boxes = [Box(b0)]
    for _ in range(N - 1):
        b = boxes.pop(np.random.choice(len(boxes)))
        boxes.extend(b.split())
    return boxes

def generate_points(boxes, num_leafs, points_per_box=1):
    return [b.sample_point() for b in boxes for _ in range(points_per_box)]

def draw_boxes(ax, boxes):
    for box in boxes:
        corners = list(box.corners())
        i = np.array(min(corners))
        j = np.array(max(corners))
        delta = (j - i)
        patch = Rectangle(i, *delta, fill=False)
        ax.add_patch(patch)

def hist_test():
    np.random.seed(0)
    num_boxes = 100
    N_dim = 2
    b0 = np.array([[0, 1.0] for _ in range(N_dim)])
    T = SamplingBoxTree(b0, num_boxes)
    boxes = T.get_leafs()

    x_d = 0.4

    y = np.array([T.profile_sample([x_d]) for _ in range(1000)])

    fig, (ax_boxes, ax_hist) = plt.subplots(nrows=2)

    draw_boxes(ax_boxes, boxes)

    ax_boxes.plot([x_d, x_d], [0, 1])
    #print(np.histogram(y))
    ax_hist.hist(y, weights=[0.001 for _ in range(1000)])

    ax_boxes.set_xlabel("y(t-1)")
    ax_boxes.set_ylabel("y(t)")
    ax_boxes.set_title("Profile distribution")
    
    ax_hist.set_xlabel("y(t) | y(t-1)==0.4")
    ax_hist.set_ylabel("density")

    plt.show()

def mutation_test():
    save_dir = "/home/jdw/garageofcode/results/sampling/gif"
    np.random.seed(0)
    num_boxes = 100
    N_dim = 2
    b0 = np.array([[0, 1.0] for _ in range(N_dim)])
    T = SamplingBoxTree(b0, num_boxes)

    fig, ax = plt.subplots()
    num_iter = 0
    while True:
        print(T.entropy())
        ax.clear()
        draw_boxes(ax, T.get_leafs())
        ax.axis("off")
        plt.draw()
        plt.pause(0.01)

        path = os.path.join(save_dir, "{0:04d}.png".format(num_iter))
        plt.savefig(path)
        T.mutate()
        num_iter += 1

if __name__ == '__main__':
    #hist_test()
    mutation_test()