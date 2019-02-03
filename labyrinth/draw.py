import numpy as np
from matplotlib.patches import Rectangle

def draw_patch(ax, node, **kwargs):
    i, j = node
    patch = Rectangle((j, i), 1, 1, **kwargs)
    ax.add_patch(patch)

def draw_labyrinth(ax, L, start, end, n, m):
    draw_patch(ax, start, facecolor='g', zorder=100)
    draw_patch(ax, end, facecolor='r', zorder=100)

    ax.plot([0, m], [0, 0], 'k')
    ax.plot([0, m], [n, n], 'k')
    ax.plot([0, 0], [0, n], 'k')
    ax.plot([m, m], [0, n], 'k')

    for i in range(n):
        for j in range(m):
            if (i, j + 1) not in L[(i, j)]:
                ax.plot([j + 1, j + 1], [i, i + 1], 'k')
            if (i + 1, j) not in L[(i, j)]:
                ax.plot([j, j + 1], [i + 1, i + 1], 'k')

def draw_path(ax, nodes, **kwargs):
    i_coords, j_coords = zip(*nodes)
    ax.step(np.array(j_coords) + 0.5, np.array(i_coords) + 0.5, **kwargs)
    #for (i0, j0), (i1, j1) in zip(nodes[:-1], nodes[1:]):
    #    ax.plot([j0+.5, j1+.5], [i0+.5, i1+.5], **kwargs)