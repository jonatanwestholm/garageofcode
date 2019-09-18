import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import numpy as np
import matplotlib.pyplot as plt

from itertools import product 
from itertools import groupby as gb
import networkx as nx

from solver import get_solver


def get_graph():
    G = nx.Graph()

    for ch in "ABCDEFGH":
        G.add_node(ch, level="top")
        for i in range(4):
            G.add_node((ch, i), level="sub")

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


# tile_dot2col[tile, dot] = col
tile_dot2col = np.array([[0,1,2,3],
                         [0,1,2,3],
                         [0,2,1,3],
                         [0,2,1,3],
                         [0,2,3,1],
                         [0,2,3,1],
                         [0,3,2,1],
                         [0,3,2,1]])


def bind_to_structure(solver, X, Y):
    for loc, x_isolocs in groupby(X.items(), key=get_loc):
        x_isolocs = [(c, var) for c, var in sorted(x_isolocs)]
        y_isolocs = [(c, var) for c, var in sorted(Y.items()) if get_loc(c) == loc]
        bind_tile(solver, x_isolocs, y_isolocs)
        #exit(0)


def bind_tile(solver, tiles, dots):
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


def main():
    G = get_graph()
    N = 8
    locs = "ABCDEFGH"
    tiles = list(range(8))
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

    bind_to_structure(solver, X, Y)
    color_match_constraints(solver, G, Y)
    #exit(0)

    solver.Solve(time_limit=100)

    # presentation
    X_solved = [(ij, solver.solution_value(x)) for ij, x in X.items()]
    #print(sum([val for _, val in X_solved]))
    #print(X_solved)
    img = np.zeros([N, N])
    for (i, j, k), x in X_solved:
        i = locs.index(i)
        if x:
            img[i, j] = 1

    plt.imshow(img)
    plt.show()

if __name__ == '__main__':
    main()