import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import numpy as np
from copy import copy
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from common.utils import flatten_simple as simple
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

    def sample_point(self):
        i, j = zip(*[(i, j) for d, (i, j) in sorted(self.dim2ij.items())])
        i = np.array(i)
        j = np.array(j)
        return i + (j - i) * np.random.random([self.N])

def generate_boxes(b0, N):
    boxes = [NBox(b0)]
    for _ in range(N - 1):
        b = boxes.pop(np.random.choice(len(boxes)))
        boxes.extend(b.split())
    return boxes

def profile_sample(dim2val, boxes):
    if not isinstance(dim2val, dict):
        # if dim2val not dict, assume dim=idx
        dim2val = {dim: val for dim, val in enumerate(dim2val)}
    boxes = profile(dim2val, [box.dim2ij for box in boxes])
    box = np.random.choice(boxes)
    return NBox(box).sample_point()    

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

if __name__ == '__main__':
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    from sklearn import decomposition

    np.random.seed(0)
    num_boxes = 100
    N_dim = 2
    points_per_box = 100
    N = num_boxes*points_per_box
    b0 = np.array([[0, 1.0] for _ in range(N_dim)])
    boxes = generate_boxes(b0, num_boxes)
    points = generate_points(boxes, num_boxes, points_per_box)

    #print(profile_sample([0.1], boxes))

    fig, ax = plt.subplots()

    draw_boxes(ax, boxes)

    if points:
        coords = np.array(points)
        ax.scatter(*coords.T, s=1)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("N={} dimensions, {} points".format(N_dim, N))

    plt.show()

    #fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')

    #pca = decomposition.PCA(n_components=2)

    #reduced = pca.fit_transform(coords)

    #fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')
    #ax.scatter(*reduced.T, s=1)