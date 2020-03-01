import random
import networkx as nx
from networkx.exception import NetworkXError as nxerror
from garageofcode.common.utils import Heap, shuffled, manhattan
from garageofcode.labyrinth.utils import init_obstruction_graph, get_grid_neighbours

def obstructed_h(Obs, node, end):
    try: 
        return len(nx.shortest_path(Obs, node, end)) - 1
    except nx.exception.NetworkXNoPath:
        return len(Obs)

def anti_obstruction(G, start, end, inspection=False):
    T = nx.Graph() # the search tree
    #global Obs
    Obs = init_obstruction_graph(G) # obstruction graph
    expanded_nodes = set()
    heap = Heap()

    heap.push(((obstructed_h(Obs, start, end), 0), start))

    while heap:
        (h_node, depth), node = heap.pop()
        #nx.set_node_attributes(T, {node: h_node}, "h")
        if inspection:
            yield T
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
                Obs.remove_edge(node, neigh)
                T.add_edge(node, neigh)
                if random.random() < 1:
                    h_neigh = obstructed_h(Obs, neigh, end) + depth + 1
                else:
                    h_neigh = h_node + 1
                heap.push(((h_neigh, depth + 1), neigh))
    else:
        #print("Warning: algo did not find path from {} to {}".format(start, end))
        yield None


    dead_end_nodes = set(T.nodes) - expanded_nodes
    T.remove_nodes_from(dead_end_nodes)
    yield T


def bidirectional(G, start, end):
    T = nx.Graph() # the search tree
    Obs_forward = init_obstruction_graph(G) # obstruction graph
    Obs_backward = init_obstruction_graph(G) # obstruction graph
    expanded_nodes = set()
    seen_forward = {start}
    seen_backward = {end}
    heap = Heap()

    heap.push(((obstructed_h(Obs_forward,  start, end), 0), start))
    heap.push(((obstructed_h(Obs_backward, end, start), 0), end))

    while heap:
        (h_neigh, depth), node = heap.pop()
        #if node in expanded_nodes:
        #    continue
        expanded_nodes.add(node)
        if node in seen_forward and node in seen_backward:
            break
        for neigh in get_grid_neighbours(G, node):
            if (node, neigh) not in G.edges:
                try:
                   Obs_forward.remove_edge(node, neigh)
                except nxerror:
                    pass
                try:
                   Obs_backward.remove_edge(node, neigh)
                except nxerror:
                    pass
            if neigh not in G[node]:
                continue
            if node in seen_forward:
                seen_forward.add(neigh)
                h_neigh = obstructed_h(Obs_forward,  neigh, end) + depth + 1
            else:
                seen_backward.add(neigh)
                h_neigh = obstructed_h(Obs_backward, neigh, start) + depth + 1
            if neigh not in expanded_nodes:
                if node in seen_forward:
                    try:
                        Obs_forward.remove_edge(node, neigh)
                    except nxerror:
                        pass
                else:
                    try:
                        Obs_backward.remove_edge(node, neigh)
                    except nxerror:
                        pass
                T.add_edge(node, neigh)
                heap.push(((h_neigh, depth + 1), neigh))
                if neigh in seen_forward and neigh in seen_backward:
                    break
    else:
        yield None

    yield T
