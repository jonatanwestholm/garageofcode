import networkx as nx
import pubchempy as pcp

from common.utils import Heap

def c(*a):
    """Conjunction"""
    return "(" + "|".join(*a) + ")"

def s(*a):
    """Sequential join"""
    return "".join(*a)

aliphatic_organic = c("B", "C", "N", "O", "P", "S", "F", "Cl", "Br", "I")
aromatic_organic = c("b", "c", "n", "o", "p", "s")
element_symbols = c("H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na>"
"Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca", "Sc", "Ti", "V", "Cr",
"Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr", 
"Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", 
"In", "Sn", "Sb", "Te", "I", "Xe", "Cs", "Ba", "Hf", "Ta", "W", "Re", 
"Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", 
"Ra", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn", "Fl", "Lv", 
"La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", 
"Tm", "Yb", "Lu", "Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", 
"Cf", "Es", "Fm", "Md", "No", "Lr")
aromatic_symbols = c("b", "c", "n", "o", "p", "s", "se", "as")

element2valence = {"B" : [3], "C": [4], "N": [3, 5], "O": [2], 
                   "P": [3, 5], "S": [2, 4, 6], 
                   "F": [1], "Cl": [1], "Br": [1], "I": [1]}

#atom_pattern = "\(?[.-=#$]?\[[A-Za-z][a-z]?  \]\)"

symbol = c(element_symbols, aromatic_symbols, "*")
bracket_atom = s('\[', isotope, "?", symbol, chiral, "?", hcount, "?", charge, "?", id_num, "?", "\]")
atom = c(bracket_atom, aliphatic_organic, aromatic_organic, "*")



class SMILES_Atom:
    def __init__(self, expr, explicit_organic=False):
        #element, charge=0, isotope=None, id_num=None, hydrogens=0
        
        # parse out parentheses
        self.push = expr[0] == "("
        self.pop = expr[-1] == ")"
        if self.push:
            expr = expr[1:]
        if self.pop:
            expr = expr[:-1]




def smiles2nx(smiles):
    pass