from pysat.solvers import Solver

class SugarRush(Solver):
    def __init__(self, name="glucose4"):
        super().__init__(name=name)
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
