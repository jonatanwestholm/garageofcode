import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from sat.solver import SugarRush

def main():
    solver = SugarRush()

    a = solver.var()
    b = solver.var()
    d = solver.var()
    c = solver.var()

    cnf = [[a, -b, -c], [-a, b, -c], [-a, -b, c]]

    solver.add_clauses_from(cnf)

    solver.solve()
    #print(solver.get_model())
    #>> [-1, -2]

    for var in [a, b, c, d]:
        print("Var: {}, Value: {}".format(var, solver.solution_value(var)))
    solver.solution_value(d)
    #print(solver.get_model())

if __name__ == '__main__':
    main()