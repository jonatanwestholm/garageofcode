from common.utils import flatten_simple

from pysat.solvers import Solver
from pysat.card import CardEnc, EncType

class SugarRush(Solver):
    """
    Quality-of-life wrapper for pysat.solvers.Solver
    """
    def __init__(self, name="glucose4"):
        super().__init__(name=name)
        self.var2val = {}

    """
    Basics
    """
    def var(self):
        if self.nof_vars() == -1:
            id_num = 1
        else:
            id_num = self.nof_vars() + 1
        self.add_clause([id_num, -id_num])
        return id_num

    def add_clauses_from(self, cnf):
        return self.append_formula(cnf)        

    def _init_var2val(self):
        for var, val in enumerate(self.get_model()):
            self.var2val[var+1] = val > 0 # 1-indexed

    def solution_value(self, var):
        if not self.var2val:
            self._init_var2val()
        return self.var2val[var]

    """
    Constructs
    """
    def symmetric(self, lits, encoding=EncType.seqcounter):
        cnf = CardEnc.equals(lits=lits, 
                              encoding=encoding, 
                              top_id=self.nof_vars())
        self.add_clauses_from(cnf.clauses)