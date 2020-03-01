import random
import numpy as np

import networkx as nx

from garageofcode.common.utils import shuffled

def init_grid_graph(n, m, p):
    G = nx.Graph()
    for i in range(n):
        for j in range(m):
            G.add_node((i, j))
            if j < m - 1 and random.random() < p:
                G.add_edge((i, j), (i, j + 1))
            if i < n - 1 and random.random() < p:
                G.add_edge((i, j), (i + 1, j))
    return G

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

def connect_labyrinth(L):
    added_edges = []
    components = list(nx.connected_components(L))
    while len(components) > 1:
        components, edge = connect_components(L, components)
        added_edges.append(edge)
    return added_edges

def connect_components(L, components):
    c = random.choice(components)
    for n in shuffled(c):
        neighbours = list(get_grid_neighbours(L, n))
        for neigh in shuffled(neighbours):
            if neigh not in c:
                neigh_c = nx.node_connected_component(L, neigh)
                components.remove(c)
                components.remove(neigh_c)
                c.update(neigh_c)
                components.append(c)
                edge = (n, neigh)
                L.add_edge(*edge)
                return components, edge

def get_grid_neighbours(L, n):
    i, j = n
    for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        neigh = (i + di, j + dj)
        if neigh in L:
            yield neigh

def search_cost(algo, L, start, end):
    T = next(algo(L, start, end))
    path_nodes = nx.shortest_path(T, start, end)
    backtrack_nodes = T.nodes - set(path_nodes)
    total_edges_passed = len(path_nodes) - 1 + 2*len(backtrack_nodes)
    return total_edges_passed