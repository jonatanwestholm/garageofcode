from sentian_miami import get_solver

def main():
    solver = get_solver("CBC")

    n = 8
    r = 84
    X = [solver.IntVar(0, 1) for _ in range(1, r)]
    Y = [i**n for i in range(1, r)]
    obj = solver.Sum([x*y for x, y in zip(X, Y)])
    solver.Add(r**n - obj >= 0)
    solver.Add(solver.Sum(X[::2]) == 32)
    solver.SetObjective(r**n - obj, maximize=False)
    solver.Solve(time_limit=300, verbose=True)

    print(r**n - solver.solution_value(obj))
    i_vec = []
    for i, (x, y) in enumerate(zip(X, Y)):
        if solver.solution_value(x):
            i_vec.append(i)
    print(i_vec)
    print(sum([i**n for i in i_vec]))
    print(r**n)

if __name__ == '__main__':
    main()