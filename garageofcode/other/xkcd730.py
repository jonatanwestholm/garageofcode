import time
import numpy as np

import networkx as nx

#from garageofcode.mip.solver import get_solver
from sentian_miami import get_solver

def get_xkcd730_graph():
    G = nx.DiGraph()
    edges = [(0, 1), (0, 7), (0, 9), (0, 10),
             (1, 7), (1, 3), (1, 6),
             (3, 4), (3, 5),
             (4, 5), (4, 9),
             (5, 8),
             (6, 7), (6, 8),
             (7, 8), (7, 9), (7, 12), (7, 13), (7, 14),
             (8, 14),
             (9, 10), (9, 11),
             (10, 11),
             (11, 12), (11, 13),
             (12, 13),
             (13, 14)
             ]

    G.add_edges_from(edges)
    return G

def get_simple_graph():
    G = nx.DiGraph()
    edges = [(0, 1), (0, 2),
             (1, 2), (1, 3),
             (2, 3),
            ]
    G.add_edges_from(edges)
    return G

def get_potentials(G, s, t):
    # It's not necessary to use a MIP solver for this;
    # it's just a linear equation system.
    # But it makes for a simple formulation.

    solver = get_solver("mono")

    t0 = time.time()
    potentials = {node: solver.NumVar(lb=0) for node in G}
    currents = {e: solver.NumVar(lb=-100) for e in G.edges}

    # Edge conditions
    U0, U_1 = 1, 0
    total_potential = U0 - U_1
    solver.Add(potentials[s] == U0)
    solver.Add(potentials[t] == U_1)

    # Kirchoff's law: current is preserved in internal nodes
    for node in G:
        in_current = solver.Sum([currents[e] for e in G.in_edges(node)])
        out_current = solver.Sum([currents[e] for e in G.out_edges(node)])
        if node == s:
            total_in = out_current
        elif node == t:
            total_out = in_current
        else:
            solver.Add(in_current == out_current)

    # Ohm's law: delta U = I * R
    for e in G.edges:
        i, j = e
        Ui = potentials[i]
        Uj = potentials[j]
        Iij = currents[e]
        Rij = 1 # ignore resistance parameter for now
        solver.Add(Ui - Uj == Rij * Iij)

    t1 = time.time()
    print("Build time: {0:.3f}".format(t1 - t0))

    solver.Solve(time_limit=10, verbose=True)

    total_current = solver.solution_value(total_in)
    total_resistance = total_potential / total_current
    print("Total resistance: {0:.3f}".format(total_resistance))
    print("Total current: {0:.3f}".format(total_current))

    for node, potential in sorted(potentials.items()):
        print("{0:d}  {1:.3f}".format(node, solver.solution_value(potential)))

def main():
    np.random.seed(0)
    G = get_xkcd730_graph()
    #G = get_simple_graph()
    get_potentials(G, 0, max(G))


if __name__ == '__main__':
    main()