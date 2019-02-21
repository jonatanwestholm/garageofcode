import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import time

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
    #print(row, ":")
    t0 = time.time()
    coords = interval_selection(row, feasible, max_len=14)
    t1 = time.time()
    print("Row time: {0:.3f}".format(t1 - t0))
    score = sum([j - i + 1 for i, j in coords], 0)
    #for i, j in coords:
    #    print("\t", row[i:j+1])
    print("Row score:", sum([j - i + 1 for i, j in coords], 0))
    return score
    #print()

def main():
    fn = "/home/jdw/garageofcode/data/pizza/medium.in"
    mat = read_infile(fn)

    #[print(row) for row in mat]
    #print()
    #for row in mat:
    #    print(feasible_in_row(row))

    score = 0
    for row in mat[:10]:
        score += maximize_row(row)
    print("Total score:", score)

if __name__ == '__main__':
    main()