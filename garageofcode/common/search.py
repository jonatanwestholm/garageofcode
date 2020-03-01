import networkx as nx
from garageofcode.common.utils import Heap, shuffled, manhattan

def a_star(G, start, end, inspection=False):
    T = nx.Graph() # the search tree
    expanded_nodes = set()
    heap = Heap()
    h = lambda x: manhattan(x, end)
    depth = 0

    heap.push(((h(start) + depth, depth), start))

    while heap:
        (h_node, depth), node = heap.pop()
        if inspection:
            yield T
        if node in expanded_nodes:
            continue
        expanded_nodes.add(node)
        if node == end:
            break
        for neigh in shuffled(G[node]):
            if neigh not in expanded_nodes:
                T.add_edge(node, neigh)
                heap.push(((h(neigh) + depth + 1, depth + 1), neigh))
    else:
        print("Warning: A* did not find path from {} to {}".format(start, end))

    dead_end_nodes = set(T.nodes) - expanded_nodes
    T.remove_nodes_from(dead_end_nodes)
    yield T

def bfs(G, start, end, inspection=False):
    T = nx.Graph() # the search tree
    expanded_nodes = set()
    heap = Heap()

    heap.push((0, start))

    while heap:
        depth, node = heap.pop()
        if inspection:
            yield T
        if node in expanded_nodes:
            continue
        expanded_nodes.add(node)
        if node == end:
            break
        for neigh in shuffled(G[node]):
            if neigh not in expanded_nodes:
                T.add_edge(node, neigh)
                heap.push((depth + 1, neigh))
    else:
        print("Warning: bfs did not find path from {} to {}".format(start, end))

    dead_end_nodes = set(T.nodes) - expanded_nodes
    T.remove_nodes_from(dead_end_nodes)
    yield T

def dfs(G, start, end, inspection=False):
    T = nx.Graph() # the search tree
    expanded_nodes = set()
    stack = [start]

    while stack:
        node = stack.pop()
        if inspection:
            yield T
        if node in expanded_nodes:
            continue
        expanded_nodes.add(node)
        if node == end:
            break
        for neigh in shuffled(G[node]):
            if neigh not in expanded_nodes:
                T.add_edge(node, neigh)
                stack.append(neigh)
    else:
        print("Warning: dfs did not find path from {} to {}".format(start, end))

    dead_end_nodes = set(T.nodes) - expanded_nodes
    T.remove_nodes_from(dead_end_nodes)
    yield T
