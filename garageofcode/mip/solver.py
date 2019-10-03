import time

from ortools.linear_solver import pywraplp

status2str = ["OPTIMAL", "FEASIBLE", "INFEASIBLE", "UNBOUNDED", "ABNORMAL", "MODEL_INVALID", "NOT_SOLVED"]

def get_solver(solver_version):
    if solver_version == "CBC":
        return SolverOrtools()

def solution_value(variable):
    return variable.solution_value()

class SolverOrtools(pywraplp.Solver):
    def __init__(self):
        super().__init__("", pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
        self.inf = self.infinity()

    def IntVar(self, lb=None, ub=None, name=""):
        if lb is None:
            lb = self.inf
        if ub is None:
            ub = self.inf
        return super().IntVar(lb, ub, name)

    def NumVar(self, lb=None, ub=None, name=""):
        if lb is None:
            lb = self.inf
        if ub is None:
            ub = self.inf
        return super().NumVar(lb, ub, name)

    def Dot(self, X, Y):
        return self.Sum([x * y for x, y in zip(X, Y)])

    def SetObjective(self, expr, maximize):
        if maximize:
            self.Maximize(expr)
        else:
            self.Minimize(expr)

    def Solve(self, time_limit=0, verbose=True):
        self.set_time_limit(time_limit*1000)
        t0 = time.time()
        status = super().Solve()
        t1 = time.time()
        if verbose:
            print("Status {0:s}".format(status2str[status]))
            print("Time: {0:.3f}".format(t1 - t0))
        return status

    def solution_value(self, variable):
        return variable.solution_value()
