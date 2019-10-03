from common.utils import flatten_simple as flatten
from common.utils import dbg

from pysat.solvers import Solver
from pysat.card import CardEnc, EncType, ITotalizer
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

    def add_lits_from(self, cnf):
        self.add_lits(flatten(cnf))

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

    def print_values(self):
        for var, val in sorted(self.var2val.items()):
            print("{}: {}".format(var, val))


    """
    Constructs
    """
    def equals(self, lits, bound=1, encoding=EncType.seqcounter):
        cnf = CardEnc.equals(lits=lits,
                             bound=bound,
                             encoding=encoding,
                             top_id=self.top_id())
        clauses = cnf.clauses
        self.add_lits_from(clauses)
        return clauses

    def atmost(self, lits, bound=1, encoding=EncType.seqcounter):
        cnf = CardEnc.atmost(lits=lits,
                             bound=bound,
                             encoding=encoding,
                             top_id=self.top_id())
        clauses = cnf.clauses
        self.add_lits_from(clauses)
        return clauses
        #self.add(clauses)
        #return cnf.clauses

    def negate(self, clauses):
        cnf = CNF(from_clauses=clauses)
        neg = cnf.negate(topv=self.top_id())
        neg_clauses = neg.clauses
        self.add_lits_from(neg_clauses)
        #neg_force = [[-auxvar] for auxvar in neg.auxvars]
        #print(neg_force)
        #self.add(neg_force)
        #print(neg.auxvars)
        #self.add([neg.auxvars])
        return neg_clauses

    def indicator(self, clauses):
        p = self.var()
        right_imp = [clause + [-p] for clause in clauses]
        left_imp = [[-lit for lit in flatten(clauses)] + [p]]
        equiv = left_imp + right_imp
        return p, equiv

    def disjunction(self, cnfs):
        inds = []
        clauses = []
        for cnf in cnfs:
            p, equiv = self.indicator(cnf)
            inds.append(p)
            clauses.extend(equiv)
        clauses.append(inds)
        return clauses

    def itotalizer(self, lits, ubound=None):
        if ubound is None:
            ubound = len(lits)
        itot = ITotalizer(lits, ubound)
        clauses = itot.cnf.clauses
        bound_vars = itot.rhs
        self.add_lits_from(clauses)
        return clauses, bound_vars

    def optimize(self, itot, debug=False):
        """
        Performs binary search
        It is assumed that
            i < j -> satisfiable(i) <= satisfiable(j)
        Where
            satisfiable(i) = self.solve(assumptions=[-i])
        """
        upper = len(itot) - 1 # smallest known to be feasible
        lower = 0 # largest known to be infeasible (after initial check)
        if not self.solve(assumptions=[-itot[upper]]):
            return None
        if self.solve(assumptions=[-itot[lower]]):
            return 0
        while True:
            mid = (upper + lower) // 2
            dbg("upper: %d" % upper, debug)
            dbg("mid: %d" % mid, debug)
            dbg("lower: %d" % lower, debug)
            if mid == lower:
                break
            satisfiable = self.solve(assumptions=[-itot[mid]])
            dbg("satisfiable: %d" % satisfiable, debug)
            if satisfiable:
                upper = mid
            else:
                lower = mid
            dbg("", debug)
        self.solve(assumptions=[-itot[upper]])
        return upper