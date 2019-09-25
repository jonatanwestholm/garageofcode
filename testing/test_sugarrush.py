import os
os.system("sudo pip3 install -e /home/jdw/projects/sugarrush/code/")

from sugarrush.solver import SugarRush

with SugarRush() as solver:
    X = [solver.var() for _ in range(6)]
    cnf = [X[:3], X[3:]]
    p, equiv = solver.indicator(cnf)
    print(equiv)
    solver.add(equiv)
    solver.add([p])
    solver.add([[-x] for x in X[:-1]])
    res = solver.solve()
    print("Satisfiable:", res)
    if res:
        print(solver.solution_values(X))
        print(solver.solution_value(p))