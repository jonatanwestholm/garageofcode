from common.utils import flatten_simple as flatten

from pysat.solvers import Solver
from pysat.card import CardEnc, EncType
from pysat.formula import CNF

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
            self.var2val[var+1] = (val > 0) * 1 # 1-indexed

    def solution_value(self, var):
        if not self.var2val:
            self._init_var2val()
        return self.var2val[var]

    def solution_values(self, variables):
        return [self.solution_value(var) for var in variables]

    def print_stats(self):
        print("Nof variables:", self.nof_vars())
        print("Nof clauses:", self.nof_clauses())

    """
    Constructs
    """
    def equals(self, lits, bound=1, encoding=EncType.seqcounter):
        cnf = CardEnc.equals(lits=lits,
                              bound=bound,
                              encoding=encoding,
                              top_id=self.top_id())
        clauses = cnf.clauses
        self.add_lits(flatten(clauses))
        return clauses
        #self.add(clauses)
        #return cnf.clauses

    def negate(self, clauses):
        cnf = CNF(from_clauses=clauses)
        neg = cnf.negate(topv=self.top_id())
        neg_clauses = neg.clauses
        self.add_lits(flatten(neg_clauses))
        return neg_clauses

    def disjunction(self, cnfs):
        return self.negate([self.negate(cnf) for cnf in cnfs])