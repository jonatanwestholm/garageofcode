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
                

def main():
    atoms = (2, 2, 2)
    target = 6
    unitary_ops = [srqt, factorial]
    merge_ops = [add, sub, mul, div]

    tree = search(atoms, target, unitary_ops, merge_ops)

if __name__ == '__main__':
    main()