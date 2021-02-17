#from collections import defaultdict
#from itertools import chain, combinations

from sugarrush.solver import SugarRush

from garageofcode.tools.main import powerset
from garageofcode.common.utils import flatten_simple

def equivalent(solver, a, b):
    """Given two cnfs a and b (in the same variables),
    determine if they are equivalent,
    or if there is some assignment to the variables,
    such that a is true and b is false, or vice versa

    solver = SugarRush()

    x1 = solver.var()
    x2 = solver.var()
    a = [[x1, x2], [x1, -x2]]
    b = [[x1]]

    Problem: auxilliary variables are present in all but 
      the simplest models.
    Extended equivalent: take in also set of main lits x,
      and iterate over all solutions to a, see with 
      assumptions if they b can be sat with those too,
      and then do vice versa for solutions to b. 
    """

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

def purelit_propagation(cnf, core):
    while True:
        pure_lits = []
        lits = set(flatten_simple(cnf))
        for lit in lits:
            if -lit not in lits and abs(lit) not in core:
                pure_lits.append(lit)

        keep_cnf = []
        for clause in cnf:
            for lit in pure_lits:
                if lit in clause:
                    break
            else:
                keep_cnf.append(clause)

        cnf = keep_cnf

        if not len(pure_lits) or not len(cnf):
            break
    return cnf

def unary_propagation(cnf, core):
    #print("original:", cnf)
    while True:
        orig_len = len(cnf)
        cnf = unit_propagation(cnf)
        #print("after unit:", cnf)
        cnf = purelit_propagation(cnf, core)
        #print("after pure:", cnf)
        if orig_len == len(cnf):
            break
    return cnf

def to_binary(N, n, a):
    n = n % 2**N
    b = "{1:0{0:d}b}".format(N, n)
    return [ap if bp == '1' else -ap for bp, ap in zip(b, a)]    

def all_equal(a):
    """Constrains all elements
    of a to be either 0 or 1
    """

    cnf = []
    for a0, a1 in zip(a, a[1:]):
        cnf.extend([[a0, -a1], [-a0, a1]])
    return cnf

def mergesort(solver, X):
    if len(X) == 1:
        return X, []
    mid = len(X) // 2
    x1, cnf1 = mergesort(solver, X[:mid])
    x2, cnf2 = mergesort(solver, X[mid:])
    z , cnfz  = merge(solver, x1, x2)
    return z, cnf1 + cnf2 + cnfz

def merge(solver, X, Y):
    N = len(X)
    M = len(Y)
    W = [[None] + Y] + \
        [[x] + [solver.var() for _ in range(M)] for _, x in enumerate(X)]

    cnf = []
    for i in range(1, N+1):
        for j in range(1, M+1):
            cnf.extend([[-W[i-1][j], -W[i][j-1], W[i][j]], 
                        [-W[i][j], W[i-1][j]],
                        [-W[i][j], W[i][j-1]]
                       ])
    Z = []
    for k in range(1, N+M+1):
        ws = [W[i][k-i] for i in range(k+1) if (0 <= k-i <= M) and (0 <= i <= N)]
        #print(k, ws)
        z, z_bind = solver.indicate_disjunction(ws)
        #print(z, z_bind)
        cnf.extend(z_bind)
        Z.append(z)
    return Z, cnf


def vsum(solver, X):
    if len(X) == 1:
        return X, []

    if len(X) == 2:
        x0, x1 = X
        t0, cnf0 = solver.xor(x0, x1)
        t1, cnf1 = solver.indicate_conjunction([x0, x1])
        return [t1, t0], cnf0 + cnf1

    mid = len(X) // 2
    t0, cnf0 = vsum(solver, X[:mid])
    t1, cnf1 = vsum(solver, X[mid:])
    n = max(len(t0), len(t1)) + 1
    pad0 = [solver.var() for _ in range(len(t1) + 1 - len(t0))]
    pad1 = [solver.var()]
    t0 = pad0 + t0
    t1 = pad1 + t1
    cnfpad = [[-p] for p in pad0 + pad1]
    z = [solver.var() for _ in range(n)]
    cnfz = solver.plus(t0, t1, z)
    return z, cnf0 + cnf1 + cnfz + cnfpad


def main():
    solver = SugarRush()

    N = 16
    X = [solver.var() for _ in range(N)]

    z, cnf = vsum(solver, X)
    zlen = len(z)
    print("zlen:", zlen)
    '''
    solver.add(cnf)
    solver.add([[zi] for zi in z[2:]])
    satisfiable = solver.solve()
    if satisfiable:
        z_solve = [(solver.solution_value(zp) > 0)*1 for zp in z]
        print(z_solve)
        z_int = sum([2**i * zp for i, zp in enumerate(z_solve[::-1])])
        print("z:", z_int)
        print([solver.solution_value(x) for x in X])
    else:
        print("not satisfiable")
    '''

    for r in range(64):
        tl, cnfl = solver.less(z, r)
        print(r, len(unary_propagation(cnf + cnfl + [[-tl]], core=X)))

        # for r > N it should be empty!

    '''

    Z, cnf = mergesort(solver, X)
    print(len(cnf))
    solver.add(cnf)

    #solver.solve(assumptions=[-X[0], -X[1], X[2], -X[3]])
    #print([solver.solution_value(z) for z in Z])

    # how many clauses would it take to do it the naive way?
    for enc in [1, 2, 3, 6, 8]:
        print("enc:", enc)
        print([len(solver.atmost(X, r, encoding=enc)) for r in range(N)])
        print()


    # testing epistemic efficiency - do 
    #  assumptions propagate to the new 
    #  full state of knowledge?

    #c = [[1, 2], [-2, 3], [-3, 2]]
    #print(purelit_propagation(c))


    r = 4
    N = 10
    X = [solver.var() for _ in range(N)]
    #for enc in [1]:
    for enc in [1, 2, 3, 6, 8]:
        original = [len(unary_propagation(solver.equals(X[:n], r, encoding=enc), core=X[:n])) for n in range(r+1, N)]
        reduced = [len(unary_propagation(solver.equals(X[:n+1], r, encoding=enc) + [[-1]], core=X[:n+1])) for n in range(r+1, N)]
        print("enc:", enc)
        print("original:", original)
        print("reduced: ", reduced)
        print()


    N = 8
    K = 4

    #a = [solver.var() for _ in range(K)]
    a = 100
    z = [solver.var() for _ in range(N)]
    v = [[solver.var() for _ in range(N)] for _ in range(2**K)]

    v0_assumptions = to_binary(N, 2, v[0])
    for v0, v1 in zip(v, v[1:]):
        solver.add(solver.plus(v0, 3, v1))

    solver.add(solver.element(v, a, z))

    #a_int = 3
    #a_assumptions = to_binary(K, a_int, a)

    #solver.solve(assumptions= v0_assumptions + a_assumptions)
    solver.solve(assumptions = v0_assumptions)

    z_solve = [(solver.solution_value(zp) > 0)*1 for zp in z]
    z_int = sum([2**i * zp for i, zp in enumerate(z_solve[::-1])])

    solver.print_stats()

    print("v[{0:d}] = {1:d}".format(a, z_int))

    K = 2
    N = 2
    a = [solver.var() for _ in range(K)]
    z = [solver.var() for _ in range(N)]
    v = [[solver.var() for _ in range(N)] for _ in range(2**K)]
    v_assumptions = [-v[0][0], -v[0][1],
                     -v[1][0],  v[1][1],
                      v[2][0], -v[2][1],
                      v[3][0],  v[3][1]]

    cnf = element(solver, v, a, z)
    solver.add(cnf)

    a_assumptions = [a[0], a[1]]
    solver.solve(assumptions= v_assumptions + a_assumptions)

    z_solve = [(solver.solution_value(zp) > 0)*1 for zp in z]
    z_int = sum([2**i * zp for i, zp in enumerate(z_solve[::-1])])

    print("z =", z_int)

    x1 = solver.var()
    x2 = solver.var()

    cnf = [[x1, x2], [-x1, -x2]]

    x = [solver.var() for _ in range(10)]
    cnf = all_equal(x)

    print(cnf)
    ext = cnf + [[-x[5]]]
    print(unit_propagation(ext))
    '''

    '''
    N = 8
    a = [solver.var() for _ in range(N)]
    # b = [solver.var() for _ in range(N)]
    z = [solver.var() for _ in range(N)]

    a_assumptions = to_binary(N, 2, a)
    # b_assumptions = to_binary(N, 1, b)

    cnf = solver.plus(a, 12, z)
    #solver.leq(a, b)
    solver.add(cnf)

    satisfiable = solver.solve(assumptions = a_assumptions)
    if satisfiable:
        z_solve = [(solver.solution_value(zp) > 0)*1 for zp in z]
        z_int = sum([2**i * zp for i, zp in enumerate(z_solve[::-1])])

        print("a + b =", z_int)
    else:
        print("not satisfiable")
    '''

    '''
    solver.leq(a, b)

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