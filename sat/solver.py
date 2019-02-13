from pysat.solvers import Glucose4, Minisat22

def get_solver(solver_name):
    if solver_name == "Glucose4":
        return SugarRush_Glucose4()
    elif solver_name == "Minisat22":
        return SugarRush_Minisat22()

class SugarRush():
    def __init__(self):
        self.var_num = 0
        self.var2val = {}
        
    def var(self):
        self.var_num += 1
        return self.var_num

    def add_clauses_from(self, cnf):
        return self.append_formula(cnf)        

    def _init_var2val(self):
        for var, val in enumerate(self.get_model()):
            self.var2val[var+1] = val > 0 # 1-indexed

    def solution_value(self, var):
        if not self.var2val:
            self._init_var2val()
        return self.var2val[var]

class SugarRush_Glucose4(Glucose4, SugarRush):
    def __init__(self):
        Glucose4.__init__(self)
        SugarRush.__init__(self)

class SugarRush_Minisat22(Minisat22, SugarRush):
    def __init__(self):
        Minisat22.__init__(self)
        SugarRush.__init__(self)