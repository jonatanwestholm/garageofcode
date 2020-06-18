import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from sentian_miami import get_solver


def mip_optimize(Y):
    #Y = [2, 6, 5, 3, 4, 5, 1]
    N = len(Y)

    solver = get_solver("CBC")

    X = {(i, j): solver.IntVar(lb=0) for i in range(N) for j in range(i+1, N+1)}

    # get exact covers
    for k, y in enumerate(Y):
        X_covering = [val for (i, j), val in X.items() if i <= k < j]
        solver.Add(solver.Sum(X_covering) == y)

    # set objective
    cost = solver.Sum(X.values())
    solver.SetObjective(cost, maximize=False)

    solver.Solve(time_limit=10)

    return solver.solution_value(cost)
    
    '''
    print("Score:", solver.solution_value(cost))
    
    height = 0
    fig, ax = plt.subplots()
    for (i, j), val in X.items():
        if solver.solution_value(val):
            #print(i, j)
            patch = Rectangle((i, height), j-i, 1)
            ax.add_patch(patch)
            height += 1

    plt.show()
    '''


def sw_optimize(Y):
    """
    Don't optimize, just return the score
    """
    #grad = np.diff(np.concatenate([[0], Y]))
    #return np.sum(grad * (grad > 0))
    return sum(x1 - x0 for x0, x1 in zip(Y, Y[1:]) if x1 > x0) + Y[0]


def main():
    for _ in range(100):
        Y = np.random.randint(50, 70, size=5)
        mip_cost = int(mip_optimize(Y))
        sw_cost = int(sw_optimize(Y))
        if sw_cost < mip_cost:
            print("{0:5d}{1:5d}".format(mip_cost, sw_cost))


if __name__ == '__main__':
    main()