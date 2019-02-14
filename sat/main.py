import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from itertools import zip_longest
from collections import defaultdict

from common.utils import flatten_simple
from sat.solver import SugarRush

def langford(solver, n):
    X = [[solver.var() for _ in range(2*n - k - 2)] for k in range(n)]

    for row in X:
        solver.add(solver.symmetric(row))
        #solver.symmetric(row)

    position2covering = defaultdict(list)
    for k, row in enumerate(X):
        for i, var in enumerate(row):
            position2covering[i].append(var)
            position2covering[i + k + 2].append(var)

    for lits in position2covering.values():
        solver.add(solver.symmetric(lits))
        #solver.symmetric(lits)

    return X

def print_langford_solution(solver, X):
    position2num = {}
    for k, row in enumerate(X):
        row_solve = [solver.solution_value(var) for var in row]
        #print(row_solve)
        idx0 = row_solve.index(True)
        idx1 = idx0 + k + 2

        if idx0 in position2num:            
            print("{} already taken by {}".format(idx0, position2num[idx0]))
        else:
            position2num[idx0] = k + 1

        if idx1 in position2num:            
            print("{} already taken by {}".format(idx1, position2num[idx1]))
        else:
            position2num[idx1] = k + 1

    _, nums = zip(*sorted(position2num.items()))
    langford_str = ", ".join(map(str, nums))
    print(langford_str)

def main():
    n = 20
    solver = SugarRush()

    X = langford(solver, n)

    print("n:", n)
    print("Nof variables:", solver.nof_vars())
    print("Nof clauses:", solver.nof_clauses())

    #return

    satisfiable = solver.solve()
    print(satisfiable)
    if not satisfiable:
        return

    print_langford_solution(solver, X)

    '''
    X = [solver.var() for _ in range(20)]

    for enctype in [EncType.pairwise, EncType.seqcounter, EncType.bitwise]: 
        cnf = CardEnc.atmost(lits=X, encoding=enctype).clauses
        print(cnf)
        print()

    return

    print(cnf)

    solver.add_clauses_from(cnf)

    solver.solve()
    #print(solver.get_model())
    #>> [-1, -2]
    '''

    #for var in flatten_simple(X):
    #    print("Var: {}, Value: {}".format(var, solver.solution_value(var)))
    #print(solver.get_model())

if __name__ == '__main__':
    main()