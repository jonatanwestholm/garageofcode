from common.utils import flatten_simple

from pysat.solvers import Solver
from pysat.card import CardEnc, EncType

class SugarRush(Solver):
    """
    Quality-of-life wrapper for pysat.solvers.Solver
    """
    def __init__(self, name="glucose4"):
        super().__init__(name=name)
        #self.top_id = 0
        self.var2val = {}
        self.lits = set([0])

    """
    Basics
    """
    def var(self):
        #self.top_id += 1
        '''
        if self.nof_vars() == -1:
            id_num = 1
        else:
            id_num = self.nof_vars() + 1
        self.add([[id_num, -id_num]])
        return id_num
        '''
        self.lits.add(self.top_id() + 1)
        return self.top_id()

    #def add_clauses_from(self, cnf):
    #    return self.append_formula(cnf)        

    def add(self, cnf):
        self.append_formula(cnf)   

    def add_lits(self, lits):
        for lit in lits:
            self.lits.add(abs(lit))

    def top_id(self):
        return max(self.lits)

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
                              top_id=self.top_id())
        clauses = cnf.clauses
        self.add_lits(flatten_simple(clauses))
        return clauses
        #self.add(clauses)
        #return cnf.clauses

    def disjunction(self, cnfs):
        pass