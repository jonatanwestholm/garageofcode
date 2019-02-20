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

    select_vars = list(coord2var.values())
    cardinality = solver.equals(select_vars, bound=2)
    solver.add(cardinality)

    satisfiable = solver.solve()
    print("Satisfiable:", satisfiable)
    if not satisfiable:
        return []
    selected_coords = [coord for coord, var in coord2var.items()
                       if solver.solution_value(var)]
    return selected_coords

def main():
    sequence = [0, 0, 0, 0, 0, 0]
    feasible = lambda x: len(x) >= 2
    coords = interval_selection(sequence, feasible)
    for coord in coords:
        print(coord)

if __name__ == '__main__':
    main()