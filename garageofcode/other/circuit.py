import time
import numpy as np

import networkx as nx

from sentian_miami import get_solver


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

    solver.Solve(time_limit=10)

    total_current = solver.solution_value(total_in)
    total_resistance = total_potential / total_current
    #print("Total resistance: {0:.3f}".format(total_resistance))
    print("Total current: {0:.3f}".format(total_current))

    #for node, potential in sorted(potentials.items()):
    #    print("{0:d}  {1:.3f}".format(node, solver.solution_value(potential)))