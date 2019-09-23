import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from matplotlib.collections import PatchCollection

from itertools import product 
from itertools import groupby as gb
import networkx as nx

from solver import get_solver
from common.utils import Heap

margin = 0.2

col2rgb = {0: "r", 1: "g", 2: "b", 3: "y"}

# tile_dot2col[tile, dot] = col
tile_dot2col_simple = np.array([[0,1,2,3],
                                [3,2,1,0],
                                [3,2,1,0]])

# tile_dot2col[tile, dot] = col
tile_dot2col = np.array([[0,1,2,3],
                         [0,1,2,3],
                         [0,2,1,3],
                         [0,2,1,3],
                         [0,2,3,1],
                         [0,2,3,1],
                         [0,3,2,1],
                         [0,3,2,1]])

def get_graph_simple():
    """For debugging
    """
    G = nx.Graph()

    for ch in "ABC":
        G.add_node(ch, level="top")
        for i in range(4):
            G.add_node((ch, i), level="sub")

    G.add_edge("A", "B", sides=(1, 3), level="top")
    G.add_edge("A", "C", sides=(3, 1), level="top")

    edges_to_add = []
    for u, v, (i, j) in G.edges(data="sides"):
        e1 = ((u, i), (v, (j + 1)%4), {"level": "sub"})
        e2 = ((u, (i + 1)%4), (v, j), {"level": "sub"})
        edges_to_add.append(e1)
        edges_to_add.append(e2)

    for u, v, data in edges_to_add:
        G.add_edge(u, v, **data)

    return G


def get_graph():
    G = nx.DiGraph()

    for ch in "ABCDEFGH":
        G.add_node(ch, level="top")
        for i in range(4):
            G.add_node((ch, i), level="sub")

    G.nodes["A"]["coord"] = np.array([0, 0])
    G.nodes["B"]["coord"] = np.array([-1, -1])
    G.nodes["C"]["coord"] = np.array([0, -1])
    G.nodes["D"]["coord"] = np.array([1, -1])

    G.nodes["E"]["coord"] = np.array([-2, -2])
    G.nodes["F"]["coord"] = np.array([-1, -2])
    G.nodes["G"]["coord"] = np.array([0, -2])
    G.nodes["H"]["coord"] = np.array([-1, -3])

    for _, data in G.nodes(data=True):
        if data["level"] is not "top":
            continue
        data["coord"] = 2.05 * data["coord"].astype(float)

    G.add_edge("A", "C", sides=(2, 0))
    G.add_edge("B", "C", sides=(1, 3))
    G.add_edge("D", "C", sides=(3, 1))
    G.add_edge("G", "C", sides=(0, 2))

    G.add_edge("B", "F", sides=(2, 0))
    G.add_edge("E", "F", sides=(1, 3))
    G.add_edge("G", "F", sides=(3, 1))
    G.add_edge("H", "F", sides=(0, 2))

    for u, v, data in G.edges(data=True):
        data["level"] = "top"

    edges_to_add = []
    for u, v, (i, j) in G.edges(data="sides"):
        e1 = ((u, i), (v, (j + 1)%4), {"level": "sub"})
        e2 = ((u, (i + 1)%4), (v, j), {"level": "sub"})
        edges_to_add.append(e1)
        edges_to_add.append(e2)

    for u, v, data in edges_to_add:
        G.add_edge(u, v, **data)

    return G


def get_loc(x):
    return x[0][0]

def get_tile(x):
    return x[0][1]

def get_dot(x):
    return x[0][1]

def get_col(x):
    return x[0][2]

def groupby(iterable, key):
    yield from gb(sorted(iterable, key=key), key=key)


def bind_to_structure(solver, X, Y, tile_dot2col):
    for loc, x_isolocs in groupby(X.items(), key=get_loc):
        x_isolocs = [(c, var) for c, var in sorted(x_isolocs)]
        y_isolocs = [(c, var) for c, var in sorted(Y.items()) if get_loc(c) == loc]
        bind_tile(solver, x_isolocs, y_isolocs, tile_dot2col)
        #exit(0)


def bind_tile(solver, tiles, dots, tile_dot2col):
    for (_, tile, turn), x in tiles:
        for (_, dot, y_col), y in dots:
            x_col = tile_dot2col[tile, (dot + turn) % 4]
            #print(x_col)
            if x_col == y_col:
                solver.Add(x <= y)
            else:
                solver.Add(x + y <= 1)
        #if num_bind != 0:
        #print(num_bind)
        #print()

            #else:
            #    solver.Add(x == 1 - y)


def color_match_constraints(solver, G, Y):
    for u, v, level in G.edges(data="level"):
        if level is not "sub":
            continue
        (loc0, dot0), (loc1, dot1) = u, v
        Y0 = [var for (loc, dot, _), var in sorted(Y.items()) 
                                            if loc == loc0 and dot == dot0]
        Y1 = [var for (loc, dot, _), var in sorted(Y.items()) 
                                            if loc == loc1 and dot == dot1]

        for y0, y1 in zip(Y0, Y1):
            solver.Add(y0 == y1)


def draw_graph(ax, G):
    '''
    side2vec = np.array([[-1, 0],
                         [0, 1],
                         [1, 0],
                         [0, -1]])*2.5
    start = next(iter(G))
    G.nodes[start]["coord"] = np.array([0, 0])

    h = Heap([start])
    while h:
        node = h.pop()
        coord = G.nodes[node]["coord"]
        for neigh in G[node]:
            if "coord" in G.nodes[neigh]:
                continue
            print(G.edges[node, neigh]["sides"])
            print(G.edges[neigh, node]["sides"])
            print()
            (side, _) = G.edges[node, neigh]["sides"]
            vec = side2vec[side]
            G.nodes[neigh]["coord"] = coord + vec
            h.push(neigh)
    '''

    node2corners = {}
    for node, data in G.nodes(data=True):
        if not data["level"] == "top":
            continue
        x, y = data["coord"]
        rect = Rectangle((y - 1, x - 1), 2, 2, facecolor='k', alpha=0.8)
        ax.add_patch(rect)
        #patches.append(rect)
        corners = [(y + 1 - margin, x - 1 + margin),
                   (y + 1 - margin, x + 1 - margin),
                   (y - 1 + margin, x + 1 - margin),
                   (y - 1 + margin, x - 1 + margin)]
        node2corners[node] = corners

    '''
    for u, v, level in G.edges(data="level"):
        if level is not "sub":
            continue
        (loc0, dot0), (loc1, dot1) = u, v
        y0, x0 = node2corners[loc0][dot0]
        y1, x1 = node2corners[loc1][dot1]
        ax.plot([y0, y1], [x0, x1], color='k')
    '''

    return node2corners


def draw_solution(G, X, tile_dot2col):
    fig, ax = plt.subplots()

    node2corners = draw_graph(ax, G)

    for (loc, tile, turn), x in X:
        if not x:
            continue

        print("Drawing {}, {}, {}".format(loc, tile, turn))

        corners = node2corners[loc]
        for idx, corner in enumerate(corners):
            col = tile_dot2col[tile, (idx + turn) % 4]
            rgb = col2rgb[col]
            dot = Circle(corner, margin, facecolor=rgb)
            ax.add_patch(dot)

    for node, data in G.nodes(data=True):
        if data["level"] is not "top":
            continue
        print("Node:", node, " coord:", data["coord"])

    #p = PatchCollection(patches)
    #ax.add_collection(p)
    ax.set_xlim([-10, 10])
    ax.set_ylim([-10, 10])
    ax.set_aspect("equal")
    ax.axis("off")
    plt.show()


def main():
    global tile_dot2col
    simple = False
    if simple:
        tile_dot2col = tile_dot2col_simple
        locs = "ABC"
        G = get_graph_simple()
    else:
        locs = "ABCDEFGH"
        G = get_graph()

    tiles = list(range(len(locs)))
    turns = list(range(4))
    dots = list(range(4))
    cols = list(range(4))

    solver = get_solver("CBC")

    X = {(loc, tile, turn): solver.IntVar(0, 1) 
            for loc, tile, turn in product(locs, tiles, turns)}

    # Constraint: exactly one tile with one turn per location
    for _, isolocs in groupby(X.items(), key=get_loc):
        key, isolocs = zip(*isolocs)
        #print(key)
        solver.Add(solver.Sum(isolocs) == 1)

    # Constraint: each tile must be placed in exactly one loc
    for _, isotile in groupby(X.items(), key=get_tile):
        key, isotile = zip(*isotile)
        #print(key)
        solver.Add(solver.Sum(isotile) == 1)
    '''
    '''

    # auxilliary variables
    Y = {(loc, dot, col): solver.IntVar(0, 1) 
            for loc, dot, col in product(locs, dots, cols)}

    # these constraints are redundant, but they may help the solver
    for _, isolocs in groupby(Y.items(), key=get_loc):
        # for each loc and dot, exactly one color
        isolocs = sorted(isolocs, key=get_dot)
        for _, isodots in groupby(isolocs, key=get_dot):
            key, isodots = zip(*isodots)
            solver.Add(solver.Sum(isodots) == 1)

        # for each loc and color, on one dot exactly
        isolocs = sorted(isolocs, key=get_col)
        for _, isocols in groupby(isolocs, key=get_col):
            key, isocols = zip(*isocols)
            solver.Add(solver.Sum(isocols) == 1)
    '''
    '''

    bind_to_structure(solver, X, Y, tile_dot2col)
    color_match_constraints(solver, G, Y)
    #exit(0)

    status = solver.Solve(time_limit=100)
    if status >= 2:
        return

    # presentation
    X_solved = [(ij, solver.solution_value(x)) for ij, x in X.items()]

    draw_solution(G, X_solved, tile_dot2col)
    #print(sum([val for _, val in X_solved]))
    #print(X_solved)
    '''
    N = 8
    img = np.zeros([N, N])
    for (i, j, k), x in X_solved:
        i = locs.index(i)
        if x:
            img[i, j] = 1

    plt.imshow(img)
    plt.show()
    '''

if __name__ == '__main__':
    main()