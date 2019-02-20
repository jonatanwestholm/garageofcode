import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from common.utils import flatten_simple as flatten
from sat.assignment import interval_selection

def read_infile(fn):
    mat = []
    char2int = {"M": 0, "T": 1}
    with open(fn, "r") as f:
        lines = f.read().split("\n")
        header = lines[0]
        lines = lines[1:]
        global R
        global C
        global L 
        global H
        R, C, L, H = map(int, header.split(" "))

        for line in lines:
            mat.append([char2int[ch] for ch in line])

    return mat

def feasible(c):
    try:
        c = flatten(c)
    except Exception:
        pass
    if len(c) > H:
        return False
    if sum(c) < L:
        return False
    if len(c) - sum(c) < L:
        return False
    return True

def feasible_in_row(row):
    return [feasible(row[i:i+H]) for i in range(len(row))]

def maximize_row(row):
    coords = interval_selection(row, feasible)
    for coord in coords:
        print(coord)

def main():
    fn = "/home/jdw/garageofcode/data/pizza/small.in"
    mat = read_infile(fn)

    [print(row) for row in mat]
    print()
    for row in mat:
        print(feasible_in_row(row))

    maximize_row(mat[0])

if __name__ == '__main__':
    main()