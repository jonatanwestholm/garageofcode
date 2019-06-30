import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import time
import math
import numpy as np
import networkx as nx

from common.utils import Heap

MAX_CREDIBLE_INTERMEDIARY = 1000

def search(atoms, target, unitary_ops, merge_ops):
    """Searching to merge atoms to target with bfs
    """

    #paths = []
    G = nx.DiGraph()
    heap = Heap()
    G.add_node(tuple(atoms), visited=False)
    heap.push((0, atoms))
    root = atoms
    g_root = tuple(root)
    g_target = (target,)
    
    while heap:
        depth, atoms = heap.pop()
        g_atoms = tuple(atoms)
        #print(g_atoms)
        if G.nodes[g_atoms]["visited"]:
            continue
        G.nodes[g_atoms]["visited"] = True
        for child, op in generate_children(atoms, unitary_ops, merge_ops):
            g_child = tuple(child)
            #print("\t", g_child)
            if g_child not in G:
                G.add_node(g_child, visited=False)
            G.add_edge(g_atoms, g_child, operation=op)
            if test_target(child, target):
                continue
            if not G.nodes[g_child]["visited"]:
                heap.push((depth+1, child))
            #print(len(heap), child)

    if g_target not in G:
        return [], G
    return [nx.shortest_path(G, g_root, parent) + [g_target]
                for parent in set(G.pred[g_target])], G


    '''
    # return all paths to target
    try:
        return nx.all_simple_paths(G, tuple(root), (target,)), G
    except nx.exception.NodeNotFound:
        return [], G
    '''

def test_target(atoms, target):
    if len(atoms) > 1:
        return False
    return np.abs(atoms[0] - target) < 1e-6


def generate_children(atoms, unitary_ops, merge_ops):
    for op in unitary_ops:
        for idx, atom in enumerate(atoms):
            b = op(atom)
            if not eligible_(b):
                continue
            c = list(atoms)
            c[idx] = b
            c = tuple(c)
            yield c, op.__name__ + '_' + str(idx) + '_unitary'

    for op in merge_ops:
        for idx, (a1, a2) in enumerate(zip(atoms[:-1], atoms[1:])):
            b = op(a1, a2)
            if not eligible_(b):
                continue
            c = list(atoms)
            c[idx:idx+2] = [b]
            c = tuple(c)
            yield c, op.__name__ + '_' + str(idx) + '_merge'


def add(a1, a2):
    return a1 + a2

def sub(a1, a2):
    return a1 - a2

def mul(a1, a2):
    return a1 * a2

def div(a1, a2):
    if a2 == 0:
        return None
    return a1 / a2

def exp(a1, a2):
    if a1 == 0 and a2 < 0:
        return None
    try:
        return a1 ** a2
    except OverflowError:
        return None

def sqrt(a):
    if a < 0:
        return None
    try:
        return math.sqrt(a)
    except TypeError as e:
        print(a)
        print(len(a))
        raise e

def factorial(a):
    if a < 0:
        return None
    f = 1
    i = 0
    while i < a:
        i += 1
        f *= i
    return f

def eligible(atoms):
    return all([eligible_(a) for a in atoms])

def eligible_(a):
    if a is None:
        return False
    if a > MAX_CREDIBLE_INTERMEDIARY:
        return False
    if not is_integer(a):
        return False
    return True

def is_integer(a):
    try:
        return np.floor(float(a)) - a == 0
    except OverflowError as e:
        print(a)
        raise e

def print_expression(path, G):
    s = ""
    atoms = [str(a) for a in path[0]]
    for n0, n1 in zip(path[:-1], path[1:]):
        op_str = G[n0][n1]["operation"]
        op, idx, arity = op_str.split("_")
        idx = int(idx)
        if arity == "unitary":
            atoms[idx] = op + "(" + atoms[idx] + ")"
        elif arity == "merge":
            atoms[idx:idx+2] = [op + "(" + atoms[idx] + ", " + atoms[idx+1] + ")"]

    print(atoms[0])


def main():
    target = 6
    unitary_ops = [sqrt, factorial]
    merge_ops = [add, sub, mul, div, exp]
    print_cutoff = 25

    t0 = time.time()
    for i in range(21):
        atoms = [i]*3
        paths, G = search(atoms, target, unitary_ops, merge_ops)
        print(i, "searched nodes: {}".format(len(G)))
        #print(path)
        if not paths:
            print(None)
            print()
            continue
        num_solutions = 0
        for path in paths:
            if num_solutions < print_cutoff:
                print_expression(path, G)
            num_solutions += 1
        if num_solutions > print_cutoff:
            print("{} more...".format(num_solutions - print_cutoff))

        print()
    print("Total time: {0:.3f}".format(time.time() - t0))

if __name__ == '__main__':
    main()