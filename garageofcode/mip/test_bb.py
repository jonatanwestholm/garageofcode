from babelsberg import get_solver

solver = None

def in_hull(u, V, **kwargs):
    """
    Checks if u is in convex hull of V using linear programming.
    V is a list of points
    u is a point
    """
    global solver
    solver = get_solver("couenne")
    X = [solver.num_var(lb=0) for _ in range(len(V))]
    
    for V_i, u_i in zip(zip(*V), u):
        solver.add(solver.dot(V_i, X) == u_i)

    solver.add(solver.sum(X) == 1)
    solver.set_objective(X[0], maximize=False)
    return solver.solve(time_limit=10, **kwargs)

def main():
    '''
    u = [1, 1]
    V = [[0, 0],
         [0, 3],
         [3, 0]]

    print("In hull:", in_hull(u, V))
    '''

    solver = get_solver("couenne")
    x = solver.num_var(lb=0.0, ub=1.0)
    y = solver.num_var(lb=0.0, ub=1.0)
    z = x + y

    #print(x <= 1)

    #solver.add(-1 <= x + y <= 1)
    #solver.add(x <= y)
    #solver.add(x >= y)
    #[print(elem) for elem in dir()]
    solver.add(x + y <= 1)
    solver.add(x + y >= 0.3)
    solver.set_objective(x, maximize=False)

    # [print(elem) for elem in dir(solver.model)]

    print(solver.solve())
    print("x:", solver.solution_value(x))
    print("y:", solver.solution_value(y))
    print("z:", solver.solution_value(z))

if __name__ == '__main__':
    main()