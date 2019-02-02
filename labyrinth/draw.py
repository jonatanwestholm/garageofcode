from matplotlib.patches import Rectangle

def draw_labyrinth(ax, L, n, m):
    start_tile = Rectangle((0, 0), 1, 1, facecolor='g')
    end_tile = Rectangle((m - 1, n - 1), 1, 1, facecolor='r')

    ax.add_patch(start_tile)
    ax.add_patch(end_tile)

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

def draw_path(ax, nodes):
    for (i0, j0), (i1, j1) in zip(nodes[:-1], nodes[1:]):
        ax.plot([j0+.5, j1+.5], [i0+.5, i1+.5], 'r', zorder=0)