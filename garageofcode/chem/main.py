import os
import csv

from garageofcode.common.utils import get_fn

MOLNAME_COL = 0
ELEM_COL = 2
X_COL = 3
Y_COL = 4
Z_COL = 5

def write_mol(f_xyz, mol_rows):
    if not len(mol_rows):
        return
    natoms = len(mol_rows)
    name = mol_rows[0][MOLNAME_COL]
    f_xyz.write(str(natoms)+"\n")
    f_xyz.write(name+"\n")
    for row in mol_rows:
        f_xyz.write(" ".join([row[ELEM_COL], row[X_COL], row[Y_COL], row[Z_COL]])+"\n")

def csv2xyz(fn, fn_target, n_mols=None):
    with open(fn) as f_csv:
        reader = csv.reader(f_csv, delimiter=",")
        _ = next(reader) # header
        with open(fn_target, "w") as f_xyz:
            i = 0
            mol_rows = []
            mol_name_current = None
            while n_mols is None or i < n_mols:
                try:
                    row = next(reader)
                except StopIteration:
                    write_mol(f_xyz, mol_rows)
                    break
                mol_name = row[MOLNAME_COL]
                if mol_name == mol_name_current:
                    mol_rows.append(row)
                else:
                    if mol_name_current is not None:
                        i += 1
                    write_mol(f_xyz, mol_rows)
                    mol_name_current = mol_name
                    mol_rows = [row]


if __name__ == '__main__':
    fn = get_fn("chem", "structures.csv", main_dir="data")
    fn_target = get_fn("chem", "structures.xyz", main_dir="data")

    csv2xyz(fn, fn_target, n_mols=None)