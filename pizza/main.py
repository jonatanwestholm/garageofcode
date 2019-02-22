import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from common.utils import flatten_simple as flatten
from common.interval_utils import get_corners2, interval_overlap2
from sat.assignment import interval_selection, interval_selection2

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
            mat.append([char2int[ch] for ch in line if line])

    return mat

def draw_border(ax, c, **kwargs):
    corners = get_corners2(c)
    corners.append(corners[0])
    x, y = zip(*corners)
    ax.plot(x, y, **kwargs)

def draw_solution(mat, coords):
    fig, ax = plt.subplots()

    adj = 0.1

    N, M = mat.shape
    for i in range(N):
        for j in range(M):
            val = mat[i, j]
            if val:
                alpha = 0.1
            else:
                alpha = 0.9
            patch = Rectangle((i+adj, j+adj), 1-2*adj, 1-2*adj, 
                              alpha=alpha,
                              facecolor="k")
            ax.add_patch(patch)
    draw_border(ax, (0, N, 0, M), color='k', linewidth=3)

    for c0 in coords:
        for c1 in coords:
            if c0 >= c1:
                continue
            if interval_overlap2(c0, c1):
                print("Overlapping: {}, {}".format(c0, c1))

    for c in coords:
        ix, jx, iy, jy = c
        wx = jx - ix 
        wy = jy - iy
        patch = Rectangle((ix+adj, iy+adj), wx-2*adj, wy-2*adj,
                          alpha=0.5)
        ax.add_patch(patch)
        draw_border(ax, c, linewidth=1)

    plt.title("Black: M, White: T, Blue: slice \nL={}, H={}".format(L, H))
    plt.axis("off")
    plt.plot()
    plt.show()

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

def get_score(coords):
    return sum([(jx-ix) * (jy-iy) for (ix, jx, iy, jy) in coords])

def maximize_mat(mat):
    if not list(mat):
        return 0
    t0 = time.time()
    coords = interval_selection2(mat, feasible, max_width=14)
    t1 = time.time()
    #print("Mat time: {0:.3f}".format(t1 - t0))
    score = get_score(coords)
    #print("Mat score:", score)

    #print(coords)
    #draw_solution(mat, coords)

    return score

def maximize_row(row):
    #print(row, ":")
    t0 = time.time()
    score = interval_selection(row, feasible, max_len=14)
    t1 = time.time()
    #print("Row time: {0:.3f}".format(t1 - t0))
    #score = sum([j - i + 1 for i, j in coords], 0)
    #for i, j in coords:
    #    print("\t", row[i:j+1])
    #print("Row score:", sum([j - i + 1 for i, j in coords], 0))
    return 0
    #print()

def main():
    fn = "/home/jdw/garageofcode/data/pizza/medium.in"
    mat = read_infile(fn)
    mat = np.array(mat)

    res = 12
    N, M = mat.shape
    score = 0.0
    num_iters = 0
    num_elems = 0
    missed = 0
    for i in range(0, N, res):
        for j in range(0, M, res):
            submat = mat[i:i+res, j:j+res]
            subnum_elems = np.size(submat)
            subscore = maximize_mat(submat)
            submissed = subnum_elems - subscore
            num_elems += subnum_elems
            score += subscore
            missed += submissed
            num_iters += 1
            #print("Average: {0:.3f}%".format(score / num_iters / num_elems * 100))
            print("Completed: {0:.2f}%".format(num_elems / (N*M) * 100))       
            print("Missed: {}".format(missed))
    print("Total score:", score)

    #[print(row) for row in mat]
    #print()
    #for row in mat:
    #    print(feasible_in_row(row))
    '''
    score = 0
    for row in mat[:10]:
        score += maximize_row(row)
    print("Total score:", score)
    '''

if __name__ == '__main__':
    main()