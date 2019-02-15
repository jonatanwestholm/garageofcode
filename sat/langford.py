from collections import defaultdict

def langford(solver, n):
    X = [[solver.var() for _ in range(2*n - k - 2)] for k in range(n)]

    for row in X:
        solver.add(solver.equals(row))
        #solver.equals(row)

    position2covering = defaultdict(list)
    for k, row in enumerate(X):
        for i, var in enumerate(row):
            position2covering[i].append(var)
            position2covering[i + k + 2].append(var)

    for lits in position2covering.values():
        solver.add(solver.equals(lits))
        #solver.equals(lits)

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