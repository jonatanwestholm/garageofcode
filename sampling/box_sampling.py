import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import time
import random
import numpy as np
from itertools import product
from scipy.linalg import null_space
#from sklearn import decomposition
from copy import copy
import networkx as nx

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from common.utils import flatten_simple as simple
from common.utils import remove_subtree, entropy
from common.box import profile, get_corners

class NBox:
    def __init__(self, dim2ij):
        if isinstance(dim2ij, dict):
            self.dim2ij = dim2ij
        else:
            # if dim2ij not dict, assume dim=idx
            self.dim2ij = {dim: ij for dim, ij in enumerate(dim2ij)}
        self.N = len(self.dim2ij)

    def split(self):
        dim = np.random.randint(self.N)

        i, j = self.dim2ij[dim]
        mid = (i + j) / 2

        bounds0 = copy(self.dim2ij)
        bounds1 = copy(self.dim2ij)

        bounds0[dim] = (i, mid)
        bounds1[dim] = (mid, j)

        return NBox(bounds0), NBox(bounds1)

    def split_and_add_to(self, T):
        child0, child1 = self.split()
        T.add_edge(self, child0)
        T.add_edge(self, child1)

    def sample_point(self):
        i, j = zip(*[(i, j) for d, (i, j) in sorted(self.dim2ij.items())])
        i = np.array(i)
        j = np.array(j)
        return i + (j - i) * np.random.random([self.N])

    def volume(self):
        vol = 1
        for dim, (i, j) in self.dim2ij.items():
            vol *= np.abs(j - i)
        return vol

    def contains(self, dim2val):
        for dim, (i, j) in self.dim2ij.items():
            val = dim2val[dim]
            if val < i or j < val:
                return False
        return True        

    def contains_profile(self, dim2val):
        """
        contains when the value has infinite span in some 
        dimensions
        """
        for dim, val in dim2val.items():
            i, j = self.dim2ij[dim]
            if val < i or j <= val:
                return False
        return True

    def profile(self, dim2val):
        """
        Returns the expansion of the box in the 
        dimensions missing from dim2val
        """
        #if not self.contains_profile(dim2val):
        #    return {}
        return {d: (i, j) for d, (i, j) in self.dim2ij.items() 
                if d not in dim2val}

    def tuple_2(self):
        return ((i, j) for d, (i, j) in sorted(self.dim2ij.items()))

def generate_box_tree(b0, N):
    T = nx.DiGraph()
    T.add_node(NBox(b0))
    return generate_box_tree_from(T, N-1)

def generate_box_tree_from(T, N):
    leafs = [v for v, d in T.out_degree() if d == 0]
    for _ in range(N):
        idx = random.randint(0, len(leafs)-1)
        box = leafs[idx]
        leafs.remove(box)
        ch0, ch1 = box.split()
        T.add_edge(box, ch0)
        T.add_edge(box, ch1)
        leafs.append(ch0)
        leafs.append(ch1)
    return T

def num_leafs(T):
    return sum([d == 0 for v, d in T.out_degree()])

def get_leafs(T):
    return [v for v, d in T.out_degree() if d == 0]

def interval_overlap(c0, c1):
    i0, j0 = c0
    i1, j1 = c1

    i, j = max(i0, i1), min(j0, j1)
    if i < j:
        return (i, j)
    else:
        return ()

def row_transition(from_state, to_states, T):
    row = np.zeros(len(to_states))
    mid = (from_state[0] + from_state[1]) / 2
    dim2val = {0: mid}
    boxes = list(tree_profile(dim2val, T))
    get_end = lambda box: box.dim2ij[0][1]
    for box in sorted(boxes, key=get_end):
        c0 = box.profile(dim2val)
        c0 = c0[1]
        intensity = 1/(c0[1] - c0[0])/len(boxes)
        tot_len = 0
        for idx, c1 in enumerate(to_states):
            tot_len += (c1[1] - c1[0])
            overlap = interval_overlap(c0, c1)
            if overlap:
                (i, j) = overlap
                row[idx] += (j - i) * intensity
    '''
    box_bins = [box.profile(dim2val)[1] for box in boxes]
    for c10, c11 in product(box_bins, repeat=2):
        if c10 == c11:
            continue
        if interval_overlap(c10, c11):
            print("Overlapping:", c10, c11)
    '''
    #exit(0)
    #print(sum(row))
    return row

def markov_transition(T):
    boxes = get_leafs(T)
    get_start = lambda box: box.dim2ij[0][0]
    get_end = lambda box: box.dim2ij[0][1]
    #bins = list(sorted(boxes, key=get_end))
    #bins = [get_end(b) for b in bins]
    bins = [get_end(box) for box in boxes]
    bins = [min(map(get_start, boxes))] + bins
    bins = list(sorted(set(bins)))
    bins = [(b0, b1) for b0, b1 in zip(bins[:-1], bins[1:])]
    #[print(i, j) for i, j in bins]
    P = [row_transition(b, bins, T) for b in bins]
    return np.array(P)

def stationary_distribution(T):
    P = markov_transition(T)
    N = len(P)
    I = np.identity(N)
    A = P.T - I # get right-kernel
    #print(P)
    #print(A)
    #print(np.sum(P, axis=1))
    pi = null_space(A)
    pi = pi / sum(pi)
    pi = [float(item) for item in pi]
    #print(pi)
    #exit(0)
    return pi

def mutate_box_tree(T):
    T = T.copy()
    num_leafs_before = num_leafs(T)
    #print("Nodes before:", num_leafs_before)
    non_leafs = [v for v, d in T.out_degree() if d > 0]
    idx = random.randint(0, len(non_leafs)-1)
    box = non_leafs[idx]
    children = list(T[box])
    for child in children:
        remove_subtree(T, child)
    num_leafs_after = num_leafs(T)
    #print("Nodes after remove:", num_leafs_after)
    num_removed = num_leafs_before - num_leafs_after
    #print("Num removed:", num_removed)
    return generate_box_tree_from(T, num_removed)
    #incomplete = [v for v, d in T.out_degree() if d < 2]
    #random.choice(incomplete).split_and_add_to(T)
    #print("Nodes after add:", num_leafs(T))
    #print()

def box_tree_entropy(T):
    leafs = get_leafs(T)
    return entropy([box.volume() for box in leafs])

def random_choice(boxes):
    idx = random.randint(0, len(boxes)-1)
    return boxes[idx]

def generate_boxes(b0, N):
    boxes = [NBox(b0)]
    for _ in range(N - 1):
        b = boxes.pop(np.random.choice(len(boxes)))
        boxes.extend(b.split())
    return boxes

def get_root(T):
    for node, deg in T.in_degree():
        if deg == 0:
            return node
    else:
        print("Found no root!")

def tree_profile(dim2val, T):
    """
    Returns leafs of T that overlap with dim2val,
    projected onto the dimensions that are not specified in dim2val
    """
    stack = [get_root(T)]
    while stack:
        box = stack.pop()
        if box.contains_profile(dim2val):
            if not T[box]: # found a leaf
                yield box
            for child in T[box]:
                stack.append(child)

def profile_sample(dim2val, T, return_box=False):
    if not isinstance(dim2val, dict):
        # if dim2val not dict, assume dim=idx
        dim2val = {dim: val for dim, val in enumerate(dim2val)}
    #boxes = profile(dim2val, [box.dim2ij for box in boxes])
    boxes = list(tree_profile(dim2val, T))
    idx = random.randint(0, len(boxes)-1)
    box = boxes[idx]
    projected = box.profile(dim2val)
    if return_box:
        return box, NBox(projected).sample_point()
    return box.profile(dim2val)

def generate_points(boxes, num_leafs, points_per_box=1):
    return [b.sample_point() for b in boxes for _ in range(points_per_box)]

def draw_boxes(ax, boxes):
    for box in boxes:
        corners = list(get_corners(box.dim2ij))
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
    boxes = generate_boxes(b0, num_boxes)

    x_d = 0.4

    y = np.array([profile_sample([x_d], boxes) for _ in range(1000)])

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
    T = generate_box_tree(b0, num_boxes)

    fig, ax = plt.subplots()
    num_iter = 0
    while True:
        print(entropy(get_leafs(T)))
        ax.clear()
        draw_boxes(ax, T.nodes)
        ax.axis("off")
        plt.draw()
        plt.pause(0.01)

        path = os.path.join(save_dir, "{0:04d}.png".format(num_iter))
        plt.savefig(path)
        T = mutate_box_tree(T)
        num_iter += 1


if __name__ == '__main__':
    #hist_test()
    mutation_test()

    '''
    np.random.seed(0)
    num_boxes = 100
    N_dim = 2
    points_per_box = 0
    N = num_boxes*points_per_box
    b0 = np.array([[0, 1.0] for _ in range(N_dim)])
    boxes = generate_boxes(b0, num_boxes)
    points = generate_points(boxes, num_boxes, points_per_box)

    print(profile_sample([0.1], boxes))

    fig, ax = plt.subplots()

    draw_boxes(ax, boxes)

    if points:
        coords = np.array(points)
        ax.scatter(*coords.T, s=1)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("N={} dimensions, {} points".format(N_dim, N))

    plt.show()
    '''
    #fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')

    #pca = decomposition.PCA(n_components=2)

    #reduced = pca.fit_transform(coords)

    #fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')
    #ax.scatter(*reduced.T, s=1)