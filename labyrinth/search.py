import networkx as nx
from common.utils import Heap, shuffled, manhattan
from labyrinth.utils import init_obstruction_graph, get_grid_neighbours

def obstructed_h(Obs, node, end):
    return len(nx.shortest_path(Obs, node, end)) - 1

def anti_obstruction(G, start, end):
    T = nx.Graph() # the search tree
    global Obs
    Obs = init_obstruction_graph(G) # obstruction graph
    expanded_nodes = set()
    heap = Heap()

    heap.push(((obstructed_h(Obs, start, end), 0), start))

    while heap:
        (h_node, depth), node = heap.pop()
        if node in expanded_nodes:
            continue
        expanded_nodes.add(node)
        if node == end:
            break
        for neigh in get_grid_neighbours(G, node):
            if (node, neigh) not in G.edges and (node, neigh) in Obs.edges:
                Obs.remove_edge(node, neigh)
            if neigh not in G[node]:
                continue
            if neigh not in expanded_nodes:
                T.add_edge(node, neigh)
                heap.push(((obstructed_h(Obs, neigh, end) + depth + 1, depth + 1), neigh))
        '''
        for neigh in shuffled(G[node]):
            if neigh not in expanded_nodes:
                T.add_edge(node, neigh)
                heap.push((obstructed_h(Obs, neigh, end), neigh))
        '''
    else:
        print("Warning: algo did not find path from {} to {}".format(start, end))


    dead_end_nodes = set(T.nodes) - expanded_nodes
    T.remove_nodes_from(dead_end_nodes)
    return T
