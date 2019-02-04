import time
import random
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

from common.utils import flatten_simple, shuffled
from mip.solver import get_solver, solution_value
from labyrinth.draw import draw_labyrinth, draw_path, draw_search_tree
from common.search import bfs, dfs

algo2name = {bfs: "BFS", dfs: "DFS"}

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

def node_expansion_buster(L, n, m):
    for i in range(n):
        for j in range(m):
            if i < n - 1:
                L.add_edge((i, j), (i + 1, j))
            column_gate = (j % 2 == 0 and i == n - 1) or (j % 2 == 1 and i == 0)
            if j < m - 1 and column_gate:
                L.add_edge((i, j), (i, j + 1))

def bfs_buster(L, n, m):
    for i in range(n):
        for j in range(m):
            if j < m - 2:
                L.add_edge((i, j), (i, j + 1))
            if (j == 0 or j == m - 1) and i < n - 1:
                L.add_edge((i, j), (i + 1, j))

    L.add_edge((0, m - 2), (0, m - 1))

def complicate_labyrinth(algo, L, start, end, num_iter=5000):
    best_cost = search_cost(algo, L, start, end)
    print("Initial cost:", best_cost)
    for i in range(num_iter):
        if i % 1000 == 0:
            print("iter", i)
        removed_edges = random.sample(list(L.edges), 4)
        L.remove_edges_from(removed_edges)
        #print(edge)
        added_edges = connect_labyrinth(L)
        new_cost = search_cost(algo, L, start, end)
        if new_cost >= best_cost:
            if new_cost > best_cost:
                print("New best cost:", new_cost)
            best_cost = new_cost
            continue
        else:
            # revert changes
            L.remove_edges_from(added_edges)
            L.add_edges_from(removed_edges)
    #print(len(L))

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

def search_cost(algo, L, start, end):
    T = algo(L, start, end)
    path_nodes = nx.shortest_path(T, start, end)
    backtrack_nodes = T.nodes - set(path_nodes)
    total_edges_passed = len(path_nodes) - 1 + 2*len(backtrack_nodes)
    return total_edges_passed

def search_score(algo, L, start, end):
    T = algo(L, start, end)
    path_nodes = nx.shortest_path(T, start, end)
    backtrack_nodes = T.nodes - set(path_nodes)
    total_edges_passed = len(path_nodes) - 1 + 2*len(backtrack_nodes)
    return len(path_nodes), total_edges_passed

def mc_search_score(algo, N, M, num_iter, start, end):
    path_lengths = []
    costs = []
    for _ in range(num_iter):
        random.seed(time.time())
        L = init_grid_graph(N, M, p=0)
        connect_labyrinth(L)
        random.seed(time.time())
        path_len, cost = search_score(algo, L, start, end)
        path_lengths.append(path_len)
        costs.append(cost)

    path_lengths = np.array(path_lengths)
    costs = np.array(costs)

    path_avg = np.mean(path_lengths)
    path_std = np.std(path_lengths)
    cost_avg = np.mean(costs)
    cost_std = np.std(costs)

    print("{0:s}, empirical figures, {1:d} iterations".format(algo2name[algo], num_iter))
    print("N={0:d}, M={1:d}".format(N, M))
    print("Path length avg: {0:.1f}, std: {1:.1f}".format(path_avg, path_std))
    print("Search cost avg: {0:.1f}, std: {1:.1f}".format(cost_avg, cost_std))

def main_draw_search_tree(ax, T, start=None, end=None):
    draw_search_tree(ax, T, zorder=0, c='r')

    if start is None or end is None:
        return ""

    path_nodes = nx.shortest_path(T, start, end)
    draw_path(ax, path_nodes, zorder=99, c='b', linewidth=3)

    backtrack_nodes = T.nodes - set(path_nodes)
    total_edges_passed = len(path_nodes) - 1 + 2*len(backtrack_nodes) 

    #plt.title("Expected nbr of steps: {0:.0f}".format(e_steps))
    title = ["Direct path nodes: {0:d}".format(len(path_nodes)),
            "Dead end nodes: {0:d}".format(len(backtrack_nodes)),
            "Total edges passed: {0:d} - 1 + 2*{1:d} = {2:d}".format(
                                    len(path_nodes),
                                    len(backtrack_nodes),
                                    total_edges_passed)]
    return "\n".join(title)

def main():
    #random.seed(1)
    N = 10
    M = N
    start = (0, 0)
    end = (0, 1)

    #mc_search_score(bfs, N, M, 1000, start, end)
    #return

    L = init_grid_graph(N, M, p=0)

    t0 = time.time()
    #bfs_buster(L, N, M)
    connect_labyrinth(L)
    t1 = time.time()
    print("Is tree:", nx.is_tree(L))
    print("Is connected:", nx.is_connected(L))
    print("Time: {0:.3f}s".format(t1 - t0))
    #bfs_buster(L, N, M)
    #return

    complicate_labyrinth(bfs, L, start, end)

    #print("End found at depth:", depth)
    #print("Nbr expanded nodes:", num_expanded)
    random.seed(time.time())

    T = bfs(L, start, end)

    #return

    fig, ax = plt.subplots()

    draw_labyrinth(ax, L, start, end, N, M)
    title = main_draw_search_tree(ax, T, start, end)

    plt.title(title)
    plt.axis("off")
    plt.show()

if __name__ == '__main__':
    main()