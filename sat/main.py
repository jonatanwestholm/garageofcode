import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from pysat.card import EncType

from sat.solver import SugarRush
from sat.langford import langford, print_langford_solution

def langford_test(n):
    with SugarRush() as solver:
        X = langford(solver, n)

        print("n:", n)
        solver.print_stats()

        satisfiable = solver.solve()
        print("Satisfiable:", satisfiable)
        if not satisfiable:
            return

        print_langford_solution(solver, X)

def negate_test():
    n = 3

    solver = SugarRush()

    X = [solver.var() for _ in range(n)]

    print(solver.top_id())
    bound_X = solver.equals(X, bound=1) #, encoding=EncType.pairwise)
    print(bound_X)
    print(solver.top_id())
    bound_X_neg = solver.negate(bound_X)
    print(bound_X_neg)
    print(solver.top_id())

    solver.add(bound_X_neg)

    solver.add([[X[0]]]) #, [-X[1]], [X[5]]])

    solver.print_stats()

    satisfiable = solver.solve()
    print("Satisfiable:", satisfiable)
    if not satisfiable:
        return

    print(solver.solution_values(X))

def main():
    #langford_test(20)

    negate_test()



if __name__ == '__main__':
    main()