import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from pysat.card import EncType

from common.utils import power_set

from sat.solver import SugarRush
from sat.langford import langford, print_langford_solution

def power_set_literals(lits):
    for subset in power_set(lits):
        yield [lit if lit in subset else -lit for lit in lits]
        #yield [1 if lit in subset else 0 for lit in lits]

def enumeration_test(solver, variables):
    satisfying_assignments = []
    unsatisfying_assignments = []
    for lits in power_set_literals(variables):
        res = solver.solve(assumptions=lits)
        bin_lits = [1 if lit > 0 else 0 for lit in lits]
        if res:
            satisfying_assignments.append(tuple(bin_lits))
        else:
            unsatisfying_assignments.append(tuple(bin_lits))

    print("Satisfying assignments:")
    [print(lits) for lits in sorted(satisfying_assignments)]
    #print(set([sum(lits[:3]) for lits in satisfying_assignments]))
    print()
    #print("False positives:")
    #[print(lits) for lits in sorted(satisfying_assignments) if sum(lits[:3]) < 2]
    

    
    print("Unsatisfying assignments:")
    #print(set([sum(lits[:3]) for lits in unsatisfying_assignments]))
    [print(lits) for lits in sorted(unsatisfying_assignments)]
    

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
    bound_X = solver.atmost(X, bound=1)
    #bound_X_neg = solver.negate(bound_X)
    solver.add(bound_X)
    #enumeration_test(solver, X)
    enumeration_test(solver, list(sorted(solver.lits - set([0]))))
    
    #print(bound_X_neg)
    #print(solver.top_id())
    #bound_X_neg_neg = solver.negate(bound_X_neg)
    #print(bound_X_neg_neg)
    #print(solver.top_id())

    #solver.add([[4]])
    #solver.add(bound_X_neg_neg)

    #solver.add([[x] for x in X])
    #solver.add([[-X[0]]]) #, [-X[1]], [X[5]]])

    #solver.print_stats()


    '''
    satisfiable = solver.solve(assumptions=[-1, 2, 3])
    print("Satisfiable:", satisfiable)
    if not satisfiable:
        return

    print(solver.solution_values(X))

    solver.print_values()
    '''

def main():
    #langford_test(20)

    negate_test()

    #for lst in power_set_literals([1, 2, 3, 4]):
    #    print(lst)



if __name__ == '__main__':
    main()