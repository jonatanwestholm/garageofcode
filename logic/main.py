import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import time
import math
import numpy as np
import networkx as nx
import pydot

from common.utils import Heap

MAX_CREDIBLE_INTERMEDIATE = 1e3
main_dir = "/home/jdw/garageofcode/results/logic"

def search(tokens, target, unary_ops, merge_ops):
    """Searching to merge tokens to target with bfs
    """

    G = nx.DiGraph()
    heap = Heap()
    G.add_node(tuple(tokens), visited=False)
    heap.push((0, tokens))
    root = tokens
    g_root = tuple(root)
    g_target = (target,)
    
    while heap:
        depth, tokens = heap.pop()
        g_tokens = tuple(tokens)
        if G.nodes[g_tokens]["visited"]:
            continue
        G.nodes[g_tokens]["visited"] = True
        for child, op in generate_children(tokens, unary_ops, merge_ops):
            g_child = tuple(child)
            if g_child not in G:
                G.add_node(g_child, visited=False)
            G.add_edge(g_tokens, g_child, operation=op)
            if test_target(child, target):
                continue
            if not G.nodes[g_child]["visited"]:
                heap.push((depth+1, child))

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

def test_target(tokens, target):
    if len(tokens) > 1:
        return False
    return np.abs(tokens[0] - target) < 1e-6


def generate_children(tokens, unary_ops, merge_ops):
    for op in unary_ops:
        for idx, token in enumerate(tokens):
            b = op(token)
            if not eligible_(b):
                continue
            c = list(tokens)
            c[idx] = b
            c = tuple(c)
            yield c, op.__name__ + '_' + str(idx) + '_unary'

    for op in merge_ops:
        for idx, (a1, a2) in enumerate(zip(tokens[:-1], tokens[1:])):
            b = op(a1, a2)
            if not eligible_(b):
                continue
            c = list(tokens)
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
        if f > MAX_CREDIBLE_INTERMEDIATE:
            return None
    return f

def eligible(tokens):
    return all([eligible_(a) for a in tokens])

def eligible_(a):
    if a is None:
        return False
    if np.abs(a) > MAX_CREDIBLE_INTERMEDIATE:
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
    tokens = [str(a) for a in path[0]]
    for n0, n1 in zip(path[:-1], path[1:]):
        op_str = G[n0][n1]["operation"]
        op, idx, arity = op_str.split("_")
        idx = int(idx)
        if arity == "unary":
            tokens[idx] = op + "(" + tokens[idx] + ")"
        elif arity == "merge":
            tokens[idx:idx+2] = [op + "(" + tokens[idx] + ", " + tokens[idx+1] + ")"]

    print(tokens[0])

def path_to_expression_graph(path, G):
    C = nx.DiGraph() # computation graph
    tokens = path[0]
    g_tokens = []
    for i, token in enumerate(tokens):
        C.add_node(str(token) + "_%d" % i, text=str(token))
        g_tokens.append(str(token) + "_%d" % i)
    
    for n0, n1 in zip(path[:-1], path[1:]):
        op_str = G[n0][n1]["operation"]
        op, idx, arity = op_str.split("_")
        idx = int(idx)
        if arity == "unary":
            old_token = g_tokens[idx]
            new_token = op + "(" + old_token + ")"
            g_tokens[idx] = new_token
            C.add_node(new_token, text=op)
            C.add_edge(old_token, new_token)
        elif arity == "merge":
            old_token0 = g_tokens[idx]
            old_token1 = g_tokens[idx+1]
            new_token = op + "(" + old_token0 + ", " + old_token1 + ")"
            g_tokens[idx:idx+2] = [new_token]
            C.add_node(new_token, text=op)
            C.add_edge(old_token0, new_token)
            C.add_edge(old_token1, new_token)

    return C

def to_png(filename, path, G):
    C = path_to_expression_graph(path, G)
    f = os.path.join(main_dir, "tmp.dot")
    nx.drawing.nx_pydot.write_dot(C, f)
    (graph,) = pydot.graph_from_dot_file(f)
    graph.write_png(filename)

def main():
    target = 6
    unary_ops = [sqrt, factorial]
    merge_ops = [add, sub, mul, div]
    print_cutoff = 1

    t0 = time.time()
    for i in range(10):
        tokens = [i]*3
        paths, G = search(tokens, target, unary_ops, merge_ops)
        print(i, "searched nodes: {}".format(len(G)))
        if not paths:
            print(None)
            print()
            continue
        num_solutions = 0
        for j, path in enumerate(paths):
            if num_solutions < print_cutoff:
                print_expression(path, G)
                filename = os.path.join(main_dir, "{}_{}.png".format(i, j))
                to_png(filename, path, G)
            num_solutions += 1
        if num_solutions > print_cutoff:
            print("{} more...".format(num_solutions - print_cutoff))

        print()
    print("Total time: {0:.3f}".format(time.time() - t0))

if __name__ == '__main__':
    main()