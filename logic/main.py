import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import numpy as np
import networkx as nx

from common.utils import Heap

def search(atoms, target, unitary_ops, merge_ops):
    """Searching to merge atoms to target with bfs
    """

    G = nx.DiGraph()
    heap = Heap()
    G.add_node(atoms, features={"visited": True})
    heap.push((0, atoms))
    root = atoms
    if atoms == target:
        return [root]

    while heap:
        _, atoms = heap.pop()
        if G.nodes[atoms]["visited"]:
            continue
        G.nodes[atoms]["visited"] = True
        for child, op in generate_children(atoms, unitary_ops, merge_ops):
            if child in G:
                continue
            G.add_node(child, {"visited": False})
            G.add_edge(atoms, child, {"operation": op})
            if child == target:
                return nx.shortest_path(G, root, child)


def generate_children(atoms, unitary_ops, merge_ops):
    for op in unitary_ops:
        for idx, atom in enumerate(atoms):
            b = op(atom)
            if not is_integer(b):
                continue
            c = list(atoms)
            c[idx] = b
            c = tuple(c)
            yield c, str(op) + _ + str(idx)

    for op in merge_ops:
        for idx, (a1, a2) in enumerate(zip(atoms[:-1], atoms[1:])):
            b = op(a1, a2)
            if not is_integer(b):
                continue
            c = list(atoms)
            c[idx:idx+2] = [b]
            c = tuple(c)
            yield c, str(op) + _ + str(idx)

def add(a1, a2):
    return a1 + a2

def sub(a1, a2):
    return a1 - a2

def mul(a1, a2):
    return a1 * a2

def div(a1, a2):
    return a1 / a2

def sqrt(a):
    return np.sqrt(a)

def factorial(a):
    f = 1
    i = 0
    while i < a:
        i += 1
        f *= i
    return f


def is_integer(a):
    return np.floor(a) - a == 0


def main():
    atoms = (2, 2, 2)
    target = 6
    unitary_ops = [sqrt, factorial]
    merge_ops = [add, sub, mul, div]

    tree = search(atoms, target, unitary_ops, merge_ops)

if __name__ == '__main__':
    main()