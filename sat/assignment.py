import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import numpy as np

from pysat.examples.fm import FM
from pysat.examples.lsu import LSU
from pysat.examples.rc2 import RC2, RC2Stratified
from pysat.formula import WCNF

from common.utils import interval_overlap
from sat.solver import SugarRush

def interval_selection(sequence, feasible, max_len=None):
    N = len(sequence)
    if not max_len:
        max_len = N
    solver = SugarRush()
    wcnf = WCNF()
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
    wcnf.extend(mutex_clauses)
    solver.add(mutex_clauses)

    if 0: # optimize number of intervals
        selected = list(coord2var.values())
        opt_vars = [-var for var in selected] # itotalizer does atmost
    elif 1: # optimize covered elements
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
        opt_vars = [-var for var in covered] # itotalizer does atmost
    
    if 0: # using ITotalizer
        #opt_vars = list(coord2var.values()) # test max num intervals
        itot_clauses, itot_vars = solver.itotalizer(opt_vars)
        solver.add(itot_clauses)
        best = solver.optimize(itot_vars, debug=False)
        if best is None:
            return []
        selected_coords = [coord for coord, var in coord2var.items()
                           if solver.solution_value(var)]
        return selected_coords
    else: # using weighted CNF and FuMalik
        #soft_clauses = [[var] for coord, var in sorted(coord2var.items())]
        #weights = [j - i + 1 for (i, j), var in sorted(coord2var.items())]
        #weights = [1 for (i, j), var in sorted(coord2var.items())]
        soft_clauses = [[-item] for item in opt_vars]
        weights = [np.random.randint(0, 5) for item in opt_vars]
        best_score = sum(weights)
        wcnf.extend(soft_clauses, weights=weights)

        #optimizer = LSU(wcnf, solver="glucose4")
        #satisfiable = optimizer.solve()
        #optimizer = FM(wcnf, solver="glucose4", enc=1)
        #optimizer = RC2Stratified(wcnf)
        optimizer = RC2(wcnf)
        satisfiable = optimizer.compute()
        #print("satisfiable:", satisfiable)
        #print("cost:", optimizer.cost)
        score = best_score - optimizer.cost
        #print("score:", score)
        #print(list(optimizer.model))
        return []
        # TODO: recover solution

def main():
    sequence = [0, 0, 0, 0, 0, 0]
    feasible = lambda x: len(x) >= 2 and len(x) <= 5
    coords = interval_selection(sequence, feasible)
    for coord in coords:
        print(coord)

if __name__ == '__main__':
    main()