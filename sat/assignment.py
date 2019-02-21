import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from common.utils import interval_overlap
from sat.solver import SugarRush

def interval_selection(sequence, feasible, max_len=None):
    N = len(sequence)
    if not max_len:
        max_len = N
    solver = SugarRush()
    coord2var = {}
    for i in range(N):
        for j in range(i, min(i + max_len, N)):
            seq = sequence[i:j+1]
            if feasible(seq):
                coord2var[(i, j)] = solver.var()

    mutex_clauses = []
    coord_2 = [(c0, c1) for c0 in coord2var for c1 in coord2var]
    for c0, c1 in coord_2:
        if c0[0] > c1[0]: # ignore symmetries
            continue
        if c0 == c1: # can't forbid overlap with self
            continue
        if interval_overlap(c0, c1):
            var0 = coord2var[c0]
            var1 = coord2var[c1]
            mutex_clauses.append([-var0, -var1])
        else:
            pass #print("Not mutually exclusive:", c0, c1)
    solver.add(mutex_clauses)

    if 0: # optimize number of intervals
        selected = list(coord2var.values())
        opt_vars = [-var for var in selected] # itotalizer can only do atmost
    else: # optimize covered elements
        idx2cov = []
        for i in range(N):
            covering = []
            for c, var in coord2var.items():
                if interval_overlap(c, (i, i)):
                    covering.append(var)
            if covering:
                idx2cov.append(covering)
        covered = []
        for covering in idx2cov:
            p, equiv = solver.indicator([covering])
            solver.add(equiv)
            covered.append(p)
        opt_vars = [-var for var in covered]
    itot_clauses, itot_vars = solver.itotalizer(opt_vars)
    solver.add(itot_clauses)

    best = solver.optimize(itot_vars, debug=False)
    if best is None:
        return []

    #satisfiable = solver.solve()
    #print("Satisfiable:", satisfiable)
    #if not satisfiable:
    #    return []
    selected_coords = [coord for coord, var in coord2var.items()
                       if solver.solution_value(var)]
    return selected_coords

def main():
    sequence = [0, 0, 0, 0, 0, 0]
    feasible = lambda x: len(x) >= 2 and len(x) <= 5
    coords = interval_selection(sequence, feasible)
    for coord in coords:
        print(coord)

if __name__ == '__main__':
    main()