import time
from minizinc import Instance, Model, Solver
import pathlib

def nqueens(solver):
    #model = Model("./nqueens.mzn")
    model = Model("./dummy.mzn")
    instance = Instance(solver, model)
    result = instance.solve()
    print(result["q"])

def staffing(solver):
    model = Model("./staffing.mzn")
    instance = Instance(solver, model)
    result = instance.solve()
    print(result["work"])

if __name__ == '__main__':
    solver = Solver.load(pathlib.Path("/home/jdw/downloads/oscar-cbls-flatzinc/fzn-oscar-cbls.msc"))
    # solver = Solver.lookup("gecode")
    t0 = time.time()

    nqueens(solver)
    #staffing(Solver)

    t1 = time.time()
    print("Total time: {0:.1f}".format(t1-t0))