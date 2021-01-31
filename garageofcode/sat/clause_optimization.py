from collections import defaultdict
from itertools import chain, combinations

from sugarrush.solver import SugarRush

from garageofcode.tools.main import powerset

def equivalent():
    solver = SugarRush()

    # Given two cnfs a and b (in the same variables),
    # determine if they are equivalent,
    # or if there is some assignment to the variables,
    # such that a is true and b is false, or vice versa
    x1 = solver.var()
    x2 = solver.var()
    a = [[x1, x2], [x1, -x2]]
    b = [[x1]]

    # get indicator variables, 
    # ta <=> a(x1, x2, ...)
    ta, ta_clauses = solver.indicator(a)
    tb, tb_clauses = solver.indicator(b)

    # see if we can find an assignment to 
    # x1, x2, ... such that XOR(ta, tb) is true
    t, xor_clauses = solver.xor(ta, tb)

    # it doesn't matter when we add the clauses,
    # or in which order.
    solver.add(ta_clauses)
    solver.add(tb_clauses)
    solver.add(xor_clauses)
    solver.add([t])

    satisfiable = solver.solve()

    if satisfiable:
        print("ta:", solver.solution_value(ta))
        print("tb:", solver.solution_value(tb))
        print("t:", solver.solution_value(t))
    else:
        print("The CNFs are equivalent")


def evaluate(cnf, var2val):
    keep_cnf = []
    for clause in cnf:
        keep_vars = []
        for var in clause:
            if var * var2val[abs(var)] > 0:
                # true literal, discard clause
                break
            elif var2val[abs(var)] == 0:
                # unknown literal, keep
                keep_vars.append(var)
            #elif var2val[abs(var)] < 0:
            #    # false literal, discard var
            #    pass
        else:
            if not len(keep_vars):
                return 0
            keep_cnf.append(keep_vars)
    if not len(keep_cnf):
        return 1
    return keep_cnf


def get_var2val(lits):
    for subset in powerset(lits):
        pwr_lits = [lit if lit in subset else -lit for lit in lits]
        var2val = defaultdict(int)
        for lit, var in zip(lits, pwr_lits):
            var2val[lit] = var
        yield var2val


def optimize(solver, cnf):
    """Given a CNF, find the smallest set of clauses
    that are equivalent to the CNF. 
    """

    # generate candidate clauses
    lits = list(set([abs(lit) for clause in cnf for lit in clause]))
    ext_lits = lits + [-lit for lit in lits]
    candidates = chain(combinations(ext_lits, 1), 
                       combinations(ext_lits, 2))
    candidates = list(candidates)

    # join candidate clauses with an enabler each
    enablers = [solver.var() for _ in candidates]
    candidates = [[-enbl] + list(candidate) 
                    for enbl, candidate in zip(enablers, candidates)]
    enbl2cand = {enbl: str(candidate[1:]) 
                    for enbl, candidate in zip(enablers, candidates)}

    # create constraints for enablers, 
    #  some can be discarded right away
    constraints = []
    for var2val in get_var2val(lits):
        resin = evaluate(candidates, var2val)
        val = evaluate(cnf, var2val)
        if val == 0:
            clause = [-lit for c in resin for lit in c]
            constraints.append(clause)
        else:
            constraints.extend(resin)
            # this case means free computation for 
            #  the solver, since we're including single-lit clauses
            # obvious optimization: remove the corresponding 
            #  enablers from candidates

    # optimize on number of enablers

    solver.add(constraints)
    satisfiable = solver.solve()

    if satisfiable:
        for enbl in enablers:
            if solver.solution_value(enbl):
                print(enbl2cand[enbl])
    else:
        print("not satisfiable")


def main():
    solver = SugarRush()

    x1 = solver.var()
    x2 = solver.var()

    cnf = [[x1, x2], [x1, -x2]]

    optimize(solver, cnf)

    '''
    var2val = defaultdict(int)
    var2val[x1] = -1
    var2val[x2] = -2
    print(evaluate(cnf, var2val))
    '''


if __name__ == '__main__':
    main()