import time
import numpy as np
import matplotlib.pyplot as plt

from garageofcode.common.utils import flatten
from garageofcode.mip.solver import get_solver, solution_value, status2str

def main():
    """
    Solve multiple exclusive shortest paths
    """
    N = 30
    T = 100
    C = np.random.random([N, N, T])

    solver = get_solver("CBC")
    X = [[[solver.IntVar(0, 1) for _ in range(N)] for _ in range(N)] for _ in range(T)]
    #X[t][i][j] = 1 if and only if transition from state i to state j at time t

    # all non-exit nodes should have exactly one outgoing
    for t in range(0, T-1):
        Xt = X[t]
        for row in Xt:
            solver.Add(solver.Sum(row) == 1)

    # all non-init nodes should have exactly one ingoing
    for t in range(1, T):
        Xt = X[t]
        for col in zip(*Xt):
            solver.Add(solver.Sum(col) == 1)

    # cost is sum of cost of used transitions
    cost = solver.Dot(flatten(X), flatten(C))
    solver.SetObjective(cost, maximize=False)

    print("solving")
    t0 = time.time()
    solver.Solve()
    print("total time: {0:.3f}".format(time.time() - t0))

    X_solved = [[[int(solution_value(X[t][i][j])) for j in range(N)] for i in range(N)] for t in range(T)]

    '''
    for Xt in X_solved:
        for row in Xt:
            print(row)
        print()
    '''

if __name__ == '__main__':
    main()