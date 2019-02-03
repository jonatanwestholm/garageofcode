import time
import random
import matplotlib.pyplot as plt
import networkx as nx

from common.utils import flatten_simple
from mip.solver import get_solver, solution_value
from labyrinth.draw import draw_labyrinth, draw_path

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

def connect_labyrinth(L):
    while not nx.is_connected(L):
        connect_components(L)

def connect_components(L):
    for c in nx.connected_components(L):
        for n in random.sample(c, len(c)):
            neighbours = list(get_grid_neighbours(L, n))
            random.shuffle(neighbours)
            for neigh in neighbours:
                if neigh not in c:
                    L.add_edge(n, neigh)
                    return  

def get_grid_neighbours(L, n):
    i, j = n
    for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        neigh = (i + di, j + dj)
        if neigh in L:
            yield neigh

def node_expansion_buster(L, n, m):
    for i in range(n):
        for j in range(m):
            if i < n - 1:
                L.add_edge((i, j), (i + 1, j))
            column_gate = (j % 2 == 0 and i == n - 1) or (j % 2 == 1 and i == 0)
            if j < m - 1 and column_gate:
                L.add_edge((i, j), (i, j + 1))

def get_labyrinth_complexity(L, start, end):
    solver = get_solver("CBC")

    node2complexity = dict([(node, solver.NumVar(lb=0)) for node in L])

    for node in L:
        expected_cost = node2complexity[node]
        if node == end:
            solver.Add(expected_cost == 0)
            continue

        num_neighs = len(L[node])
        neigh2complexity = [node2complexity[neigh] for neigh in L[node]]
        avg_neigh_complexity = solver.Sum(neigh2complexity) / num_neighs
        solver.Add(expected_cost == 1 + avg_neigh_complexity)

    solver.Solve(time_limit=10)

    return solution_value(node2complexity[start])

def main():
    random.seed(0)
    N = 10
    M = N
    start = (0, 0)
    end = (N-1, M-1)
    L = init_grid_graph(N, M, p=0)

    connect_labyrinth(L)

    e_steps = get_labyrinth_complexity(L, start, end)
    
    fig, ax = plt.subplots()

    draw_labyrinth(ax, L, N, M)
    
    nodes = nx.shortest_path(L, start, end)
    draw_path(ax, nodes)

    plt.title("Expected nbr of steps: {0:.0f}".format(e_steps))

    plt.axis("off")
    plt.show()

if __name__ == '__main__':
    main()