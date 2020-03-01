import numpy as np

import matplotlib.pyplot as plt
import networkx as nx

from garageofcode.labyrinth.utils import init_grid_graph, connect_labyrinth, search_cost
from garageofcode.labyrinth.draw import draw_labyrinth, draw_search_tree, draw_path
from garageofcode.labyrinth.search import anti_obstruction, bidirectional

N = 10
M = N
start = (0, 0)
end = (N // 2, M // 2)
L = init_grid_graph(N, M, p=0)
connect_labyrinth(L)
#algo = anti_obstruction
algo = bidirectional

fig, ax = plt.subplots()

def draw():
    plt.cla()
    #plt.pause(0.05)
    draw_labyrinth(ax, L, start, end, N, M, linewidth=5)

    T = next(algo(L, start, end))
    if T is None:
        ax.set_title("Score: ")
    else:
        draw_search_tree(ax, T, color="r")
        path = nx.shortest_path(T, start, end)
        draw_path(ax, path, color="b", linewidth=3)
        score = search_cost(algo, L, start, end)
        ax.set_title("Score: {0:d}".format(score))
    plt.axis("off")
    plt.draw()
    plt.pause(0.05)


def int_off(x):
    """
    How far is x from being an integer?
    """
    return np.abs(x - np.around(x))


def switch_edge(u, v):
    try:
        L.remove_edge(u, v)
    except nx.exception.NetworkXError:
        L.add_edge(u, v)


def onclick(event):
    x = event.xdata
    y = event.ydata
    #print(x, y)
    w = 0.15
    if ((int_off(x) <= w) + (int_off(y) <= w)) == 1:
        if int_off(x) <= w:
            #print(np.around(x), int(y))
            x0, x1 = np.around(x) - 1, np.around(x)
            y0 = int(y)
            if (y0, x0) in L and (y0, x1) in L:
                switch_edge((y0, x0), (y0, x1)) # matrix indexation
        if int_off(y) <= w:
            y0, y1 = np.around(y) - 1, np.around(y)
            x0 = int(x)
            if (y0, x0) in L and (y1, x0) in L:
                switch_edge((y0, x0), (y1, x0)) # matrix indexation
        draw()


def main():
    draw()
    #plt.axis("off")
    fig.canvas.mpl_connect("button_press_event", onclick)
    plt.show()



if __name__ == '__main__':
    main()