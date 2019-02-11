import networkx as nx
from common.utils import Heap, shuffled, manhattan

def init_obstruction_graph(G):
    i0, j0 = min(G)
    i1, j1 = max(G)
    Obs = nx.Graph()
    for i in range(i0, i1 + 1):
        for j in range(j0, j1 + 1):
            #Obs.add_node((i, j))
            if i < i1:
                Obs.add_edge((i, j), (i + 1, j))
            if j < j1:
                Obs.add_edge((i, j), (i, j + 1))
    return Obs

def obstructed_h(Obs, node, end):
    try:
        return len(nx.shortest_path(Obs, node, end)) - 1
    except:
        return 2 * manhattan(node, end)

def anti_obstruction(G, start, end):
    T = nx.Graph() # the search tree
    Obs = init_obstruction_graph(G) # obstruction graph
    expanded_nodes = set()
    heap = Heap()

    heap.push((obstructed_h(Obs, start, end), start))

    while heap:
        _, node = heap.pop()
        if node in expanded_nodes:
            continue
        expanded_nodes.add(node)
        Obs.remove_node(node)
        if node == end:
            break
        for neigh in shuffled(G[node]):
            if neigh not in expanded_nodes:
                T.add_edge(node, neigh)
                heap.push((obstructed_h(Obs, neigh, end), neigh))
    else:
        print("Warning: A* did not find path from {} to {}".format(start, end))

    dead_end_nodes = set(T.nodes) - expanded_nodes
    T.remove_nodes_from(dead_end_nodes)
    return T

def a_star(G, start, end):
    T = nx.Graph() # the search tree
    expanded_nodes = set()
    heap = Heap()
    h = lambda x: manhattan(x, end)
    depth = 0

    heap.push(((h(start) + depth, depth), start))

    while heap:
        (h_node, depth), node = heap.pop()
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
    return T

def bfs(G, start, end):
    T = nx.Graph() # the search tree
    expanded_nodes = set()
    heap = Heap()

    heap.push((0, start))

    while heap:
        depth, node = heap.pop()
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
    return T

def dfs(G, start, end):
    T = nx.Graph() # the search tree
    expanded_nodes = set()
    stack = [start]

    while stack:
        node = stack.pop()
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
    return T
