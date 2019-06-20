import numpy as np

from solver import get_solver, status2str

def is_bounded(planes):
    if not len(planes):
        return False

    solver = get_solver("CBC")

    X = [solver.NumVar(lb=-1000, ub=1000) for _ in range(len(planes[0]) - 1)]

    obj = 0
    for A in planes:
        #print(A)
        a, d = A[:-1], A[-1]
        proj = solver.Dot(a, X)
        obj += proj * np.random.random()
        solver.Add(proj >= d)

    #solver.Add(X[0] <= 1)
    #solver.Add(X[0] >= -1)

    #obj = solver.Dot(np.sum(planes[:, :-1], axis=0), X)

    solver.SetObjective(obj, maximize=True)

    result = solver.Solve(time_limit=10)

    if status2str[result] != "INFEASIBLE":
        print(status2str[result])
        print([solver.solution_value(x) for x in X])

def main():
    for _ in range(1000):
        A = np.random.random([5, 3]) - 0.5
        #A = np.array([[1, -1],
        #              [-1, -1]])

        #print(A)
        is_bounded(A)

if __name__ == '__main__':
    main()