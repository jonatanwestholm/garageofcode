from collections import defaultdict

from sugarrush.solver import SugarRush

from garageofcode.common.utils import flatten_simple

N = 4

def get_state(solver):
    # one-hot encoding
    X = [[[solver.var() for _ in range(N**2)] 
                        for _ in range(N)] 
                        for _ in range(N)]
    for x in flatten_simple(X):
        solver.add(solver.equals(x, 1)) # exactly one number per tile

    #for y in zip(*X):
    #    solver.add(solver.equals(y, 1))

    return X

def get_transition(solver, X0, X1):
    ij2swaps = defaultdict(list)
    swap2ijs = {}
    for i in range(N):
        for j in range(N):
            if j < N - 1:
                swap = solver.var()
                swap2ijs[swap] = [(i, j), (i, j+1)]
                ij2swaps[(i, j)].append(swap)
                ij2swaps[(i, j+1)].append(swap)
            if i < N - 1:
                swap = solver.var()
                swap2ijs[swap] = [(i, j), (i+1, j)]
                ij2swaps[(i, j)].append(swap)
                ij2swaps[(i+1, j)].append(swap)

    cnf = []
    for i in range(N):
        for j in range(N):
            hot = X0[i][j][0]
            # if the empty square is on (i, j) (is 'hot'), 
            # then one of the adjacent swaps must be used
            for swap in swap2ijs:
                if swap not in ij2swaps[(i, j)]:
                    cnf.append([-hot, -swap])

            cnf.append([-hot] + ij2swaps[(i, j)])

    for swap, ijs in swap2ijs.items():
        # if a swap is used, one of the adjacent
        # squares must be hot
        #cnf.append([-swap] + swap2ijs[swap])

        # if swap is true, then the adjacent tiles should swap values
        (il, jl), (ir, jr) = ijs # left/right
        for x0l, x1r in zip(X0[il][jl], X1[ir][jr]):
            # swap => x0l == x1r
            cnf.extend([[-swap, x0l, -x1r], [-swap, -x0l, x1r]])
        for x0r, x1l in zip(X0[ir][jr], X1[il][jl]):
            # swap => x0r == x1l
            cnf.extend([[-swap, x0r, -x1l], [-swap, -x0r, x1l]])

        for ij in ij2swaps:
            # if tile is not adjacent to swap,
            # then X1 = X0 in that tile
            if ij not in ijs:
                i, j = ij
                for x0, x1 in zip(X0[i][j], X1[i][j]):
                    # swap => x0 == x1
                    cnf.extend([[-swap, x0, -x1], [-swap, -x0, x1]])

    swaps = list(swap2ijs.keys())
    cnf.extend(solver.equals(swaps, 1)) # only one swap per turn
    return cnf

def set_state(X0, ij2k=None):
    cnf = []
    for i in range(N):
        for j in range(N):
            for k in range(N**2):
                if k == ij2k[(i, j)]:
                    cnf.append([X0[i][j][k]])
                else:
                    cnf.append([-X0[i][j][k]])
    return cnf

def print_solve(solver, Xr):
    Xr_solve = [[[solver.solution_value(xi) for xi in x]
                                            for x in row]
                                            for row in Xr]
    for row in Xr_solve:
        print([x.index(1) for x in row])

def main():
    for r in range(3, 24):
        solver = SugarRush()

        #r = 5 # note: r is number of steps i.e. num states minus one
        X = [get_state(solver) for _ in range(r+1)]

        ij2k = {(i, j): i * N + j for j in range(N) for i in range(N)}
        cnf = set_state(X[0], ij2k)
        solver.add(cnf)

        for X0, X1 in zip(X, X[1:]):
            cnf = get_transition(solver, X0, X1)
            solver.add(cnf)

        ij2k[(0, 1)] = 2
        ij2k[(0, 2)] = 1
        cnf = set_state(X[-1], ij2k)
        solver.add(cnf)

        satisfiable = solver.solve()
        if satisfiable:
            print(r)
            for x in X:
                print_solve(solver, x)
                print()
            return
        else:
            print(r, "not satisfiable")



if __name__ == '__main__':
    main()