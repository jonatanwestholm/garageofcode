from collections import defaultdict
from itertools import chain, combinations

from sugarrush.solver import SugarRush

from garageofcode.tools.main import powerset

def equivalent():
    """Given two cnfs a and b (in the same variables),
    determine if they are equivalent,
    or if there is some assignment to the variables,
    such that a is true and b is false, or vice versa
    """

    solver = SugarRush()

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


def evaluate(cnf, var2val, solve):
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
    if solve:
        s = SugarRush()
        s.add(keep_cnf)
        return s.solve()
    else:
        return keep_cnf


def get_var2val(lits):
    for subset in powerset(lits):
        pwr_lits = [lit if lit in subset else -lit for lit in lits]
        var2val = defaultdict(int)
        for lit, var in zip(lits, pwr_lits):
            var2val[lit] = var
        yield var2val


def optimize(solver, cnf, x, num_auxilliary=0):
    """Given a CNF, find the smallest set of clauses
    that are equivalent to the CNF. 
    """

    # generate candidate clauses
    lits = [abs(lit) for lit in x]
    aux = [solver.var() for _ in range(num_auxilliary)]
    lits.extend(aux)
    #lits = list(set([abs(lit) for clause in cnf for lit in clause]))
    ext_lits = lits + [-lit for lit in lits]
    candidates = chain(combinations(ext_lits, 1), 
                       combinations(ext_lits, 2),
                       combinations(ext_lits, 3))
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
        resin = evaluate(candidates, var2val, solve=False)
        val = evaluate(cnf, var2val, solve=True)
        if val == 0:
            clause = [-lit for c in resin for lit in c]
            constraints.append(clause)
        elif val == 1:
            constraints.extend(resin)
            # this case means free computation for 
            #  the solver, since we're including single-lit clauses
            # obvious optimization: remove the corresponding 
            #  enablers from candidates
        else:
            print("something wrong!")
            print(x)
            return

    # optimize on number of enablers
    #print(constraints)

    solver.add(constraints)
    print(solver.get_clauses())

    #solver.add(solver.atmost(enablers, 13, encoding=7))
    solver.print_stats()

    print("starting to solve")

    satisfiable = solver.solve()

    if satisfiable:
        total_enbl = 0
        for enbl in enablers:
            if solver.solution_value(enbl):
                total_enbl += 1
                print(enbl2cand[enbl])
        print("len(cnf):", len(cnf))
        print("optimized:", total_enbl)
    else:
        print("not satisfiable")


def unit_propagation(cnf):
    while True:
        unit_clause_lits = []
        for clause in cnf:
            if len(clause) == 1:
                unit_clause_lits.append(clause[0])

        keep_cnf = []
        for clause in cnf:
            for u in unit_clause_lits:
                if u in clause:
                    break
                elif -u in clause:
                    clause.remove(-u)
            else:
                keep_cnf.append(clause)

        cnf = keep_cnf

        if not len(unit_clause_lits) or not len(cnf):
            break
    return cnf

def leq(solver, a, b):
    tp_1 = None
    for ap, bp in zip(a, b):
        # if tp becomes true anywhere,
        #  then this will propagate to all subsequent clauses,
        #  and pop them
        if tp_1 is None:
            already_smaller = [[-ap], [bp]]
        else:
            already_smaller = [[tp_1, -ap], [tp_1, bp]]
        tp, tp_bind = solver.indicator(already_smaller)
        solver.add(tp_bind)
        solver.add([tp, -ap, bp]) # tp OR (ap <= bp) == (tp OR !ap OR bp)
        tp_1 = tp

def to_binary(N, n, a):
    n = n % 2**N
    b = "{1:0{0:d}b}".format(N, n)
    return [ap if bp == '1' else -ap for bp, ap in zip(b, a)]    

def plus(solver, a, b, z):
    """Constrains 
    z = a + b
    It is assumed that
    len(a) == len(b) == len(z)
    Note that z can overflow
    """

    carry = None
    for ap, bp, zp in zip(a[::-1], b[::-1], z[::-1]):
        if carry is None:
            t, t_bind = solver.parity([ap, bp])
            carry = solver.var()
            solver.add([[-carry, ap], [-carry, bp], [carry, -ap, -bp]]) # carry == ap AND bp
        else:
            t, t_bind = solver.parity([ap, bp, carry])
            carry_1 = solver.var()
            solver.add([[carry_1, -ap, -bp], [carry_1, -ap, -carry], [carry_1, -bp, -carry], 
                        [-carry_1, ap,  bp], [-carry_1, ap,  carry], [-carry_1, bp,  carry]]) 
            # carry_1 == (ap + bp + carry >= 2)
            carry = carry_1
        solver.add(t_bind)
        solver.add([[zp, -t], [-zp, t]]) # zp == t

def main():
    solver = SugarRush()

    '''
    x1 = solver.var()
    x2 = solver.var()

    cnf = [[x1, x2], [-x1, -x2]]

    x = [solver.var() for _ in range(3)]
    cnf = solver.atmost(x, 1, encoding=1)

    print(cnf)
    ext = cnf + [[3]]
    u = unit_propagation(ext)
    print(u)
    '''

    N = 8
    a = [solver.var() for _ in range(N)]
    b = [solver.var() for _ in range(N)]
    z = [solver.var() for _ in range(N)]


    a_assumptions = to_binary(N, 2, a)
    b_assumptions = to_binary(N, 1, b)

    plus(solver, a, z, b)
    #leq(solver, a, b)

    satisfiable = solver.solve(assumptions = a_assumptions + b_assumptions)
    if satisfiable:
        z_solve = [(solver.solution_value(zp) > 0)*1 for zp in z]
        z_int = sum([2**i * zp for i, zp in enumerate(z_solve[::-1])])

        print("b - a =", z_int)
    else:
        print("not satisfiable")

    '''
    leq(solver, a, b)

    for i in range(2**N - 1):
        a_assumptions = to_binary(N, i, a)
        for j in range(2**N - 1):
            b_assumptions = to_binary(N, j, b)
            satisfiable = solver.solve(assumptions = a_assumptions + b_assumptions)
            if satisfiable and (i > j):
                print("Error:", i, j)

    optimize(solver, cnf, x, num_auxilliary=0)

    var2val = defaultdict(int)
    var2val[x1] = -1
    var2val[x2] = -2
    print(evaluate(cnf, var2val))
    '''


if __name__ == '__main__':
    main()