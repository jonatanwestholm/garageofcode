import time

from sentian_miami import get_solver

def main():
    t0 = time.time()
    solver = get_solver("mono")

    a = solver.NumVar(lb=0)
    b = solver.NumVar(lb=0)

    solver.Add(2*a + b <= 1)
    solver.Add(a + 2*b <= 1)
    solver.SetObjective(a + b, maximize=True)
    t1 = time.time()

    print("Build time: {0:.3f}".format(t1 - t0))

    solver.Solve()

    a_solve = solver.solution_value(a)
    b_solve = solver.solution_value(b)

    print("a: {}".format(a_solve))
    print("b: {}".format(b_solve))


if __name__ == '__main__':
    main()