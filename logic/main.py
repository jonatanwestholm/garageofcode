import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import math
import numpy as np
import networkx as nx

from common.utils import Heap

MAX_CREDIBLE_INTERMEDIARY = 1000

def search(atoms, target, unitary_ops, merge_ops):
    """Searching to merge atoms to target with bfs
    """

    G = nx.DiGraph()
    heap = Heap()
    G.add_node(tuple(atoms), visited=False)
    heap.push((0, atoms))
    root = atoms
    if test_target(atoms, target):
        return [root]

    while heap:
        depth, atoms = heap.pop()
        g_atoms = tuple(atoms)
        #print(g_atoms)
        if G.nodes[g_atoms]["visited"]:
            continue
        G.nodes[g_atoms]["visited"] = True
        for child, op in generate_children(atoms, unitary_ops, merge_ops):
            if child in G:
                continue
            g_child = tuple(child)
            G.add_node(g_child, visited=False)
            G.add_edge(g_atoms, g_child, operation=op)
            if test_target(child, target):
                return nx.shortest_path(G, tuple(root), g_child)
            heap.push((depth+1, child))

def test_target(atoms, target):
    if len(atoms) > 1:
        return False
    return atoms[0] == target


def generate_children(atoms, unitary_ops, merge_ops):
    for op in unitary_ops:
        for idx, atom in enumerate(atoms):
            b = op(atom)
            if not eligible_(b):
                continue
            c = list(atoms)
            c[idx] = b
            c = tuple(c)
            yield c, str(op) + '_' + str(idx)

    for op in merge_ops:
        for idx, (a1, a2) in enumerate(zip(atoms[:-1], atoms[1:])):
            b = op(a1, a2)
            if not eligible_(b):
                continue
            c = list(atoms)
            c[idx:idx+2] = [b]
            c = tuple(c)
            yield c, str(op) + '_' + str(idx)

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

def main():
    target = 6
    unitary_ops = [sqrt, factorial]
    merge_ops = [add, sub, mul, div]

    for i in range(11):
        atoms = [i]*3
        tree = search(atoms, target, unitary_ops, merge_ops)
        print(tree)

if __name__ == '__main__':
    main()