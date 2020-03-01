import os
import time
import random
import numpy as np
import copy
import matplotlib.pyplot as plt
import networkx as nx

from garageofcode.mip.solver import get_solver, solution_value
from garageofcode.common.utils import flatten_simple, shuffled, manhattan, get_fn
from garageofcode.common.search import bfs, dfs, a_star
from garageofcode.labyrinth.utils import connect_labyrinth, init_grid_graph, search_cost
from garageofcode.labyrinth.draw import draw_labyrinth, draw_path, draw_search_tree, draw_obstruction_graph, draw_heuristics
from garageofcode.labyrinth.search import anti_obstruction

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

def anti_obstruction_buster(L):
    n, m = max(L)
    for i in range(n + 1):
        for j in range(m + 1):
            if i == n and j < m:
                L.add_edge((i, j), (i, j + 1))

            if i == 0 and j > 0 and j < m:
                L.add_edge((i, j), (i, j + 1))

            if i < n:
                if j == 0 or j == m or i != 0:
                    L.add_edge((i, j), (i + 1, j))

def adversarial_random(algo, L, start, end, num_iter=5000):
    best_cost = search_cost(algo, L, start, end)
    print("Initial cost:", best_cost)
    for i in range(num_iter):
        if i % 100 == 0:
            print("iter", i)
            visualize_labyrinth(algo, L, start, end, iteration=i)
        removed_edges = random.sample(list(L.edges), 4)
        L.remove_edges_from(removed_edges)
        #print(edge)
        added_edges = connect_labyrinth(L)
        new_cost = search_cost(algo, L, start, end)
        if new_cost >= best_cost:
            if new_cost > best_cost:
                print("New best cost:", new_cost)
                visualize_labyrinth(algo, L, start, end, iteration=i)
            best_cost = new_cost
            #if i % 10 == 0:
            #    visualize_labyrinth(algo, L, start, end, iteration=i)
            continue
        else:
            # revert changes
            L.remove_edges_from(added_edges)
            L.add_edges_from(removed_edges)
    #print(len(L))

def adversarial_targeted_random(algo, L, start, end, num_iter=20000):
    best_cost = search_cost(algo, L, start, end)
    old_len_sp = len(L)
    best_L = copy.deepcopy(L)
    best_iter = 0
    #print("Initial cost:", best_cost)
    for i in range(num_iter):
        if i % 100 == 0:
            pass #print("iter", i)
        T = next(algo(L, start, end))
        sp_nodes = nx.shortest_path(T, start, end)
        

        removed_edges = set()
        added_edges = set()
        remain_removed_edges = set()
        new_edges = set()

        if random.random() < 0.5:
            (i0, j0) = random.choice(sp_nodes)
            radius = 3
            for d_i in range(-radius, radius):
                for d_j in range(-radius, radius):
                    center_node = (i0 + d_i, j0 + d_j)
                    if center_node not in L:
                        continue
                    
                    right_node = (i0 + d_i, j0 + d_j + 1)
                    right_edge = (center_node, right_node)
                    rnd = random.random()
                    base = 1.4
                    if right_edge in L.edges and rnd < base**(-(1 + manhattan(center_node, right_node))):
                        removed_edges.add(right_edge)
                    elif right_node in L and rnd < 0*base**(-(2 + manhattan(center_node, right_node))):
                        added_edges.add(right_edge)
                    up_node = (i0 + d_i + 1, j0 + d_j)
                    up_edge = (center_node, up_node)
                    #rnd = random.random()
                    if up_edge in L.edges and rnd < base**(-(1 + manhattan(center_node, right_node))):
                        removed_edges.add(up_edge)
                    elif up_node in L and rnd < 0*base**(-(2 + manhattan(center_node, right_node))):
                        added_edges.add(up_edge)

            L.remove_edges_from(removed_edges)
            new_edges = connect_labyrinth(L)
            added_edges = [e for e in added_edges if e not in L]
            L.add_edges_from(added_edges)
        else:
            remain_removed_edges = random.sample(list(L.edges), 4)

        new_cost = search_cost(algo, L, start, end)
        if new_cost >= best_cost or \
                (new_cost >= best_cost - 2 and random.random() < 0.1) or \
                (new_cost >= best_cost - 10 and len(sp_nodes) < old_len_sp and random.random() < 0.1):
            if new_cost >= best_cost:
                best_L = copy.deepcopy(L)
                best_iter = i
            if new_cost > best_cost:
                print("New best cost:", new_cost)
                best_cost = new_cost
                #visualize_labyrinth(algo, L, start, end, iteration=i)
                return L
            old_len_sp = len(sp_nodes)
            if i % 50 == 0:
                pass #visualize_labyrinth(algo, L, start, end, iteration=i)
            continue
        else:
            if i > best_iter + leniency_iters:
                #backtrack to best
                L = copy.deepcopy(best_L)
            else:
                # revert changes
                L.remove_edges_from(added_edges)
                L.remove_edges_from(new_edges)
                L.add_edges_from(removed_edges)
                L.add_edges_from(remain_removed_edges)

        assert nx.is_connected(L)

    L = best_L


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

def search_score(algo, L, start, end):
    T = next(algo(L, start, end))
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

def main_draw_search_tree(ax, L, T, start=None, end=None):
    draw_search_tree(ax, T, zorder=0, c='r')

    if start is None or end is None:
        return ""

    if end in T:
        path_nodes = nx.shortest_path(T, start, end)
        draw_path(ax, path_nodes, zorder=99, c='b', linewidth=3)
    else:
        path_nodes = [start]

    backtrack_nodes = T.nodes - set(path_nodes)
    total_edges_passed = len(path_nodes) - 1 + 2*len(backtrack_nodes) 
    unexpanded_nodes = len(L) - len(T)

    #plt.title("Expected nbr of steps: {0:.0f}".format(e_steps))
    title = ["Direct path nodes: {0:d}".format(len(path_nodes)),
            "Dead end nodes: {0:d}".format(len(backtrack_nodes)),
            "Unexpanded nodes: {0:d}".format(unexpanded_nodes),
            "Total edges passed: {0:d} - 1 + 2*{1:d} = {2:d}".format(
                                    len(path_nodes),
                                    len(backtrack_nodes),
                                    total_edges_passed)]
    return "\n".join(title)


"""
algo2name = {bfs: "BFS", dfs: "DFS"}
gif_dir = get_fn("labyrinth/gif")

fig, ax = plt.subplots(figsize=(5.7, 6.5))

N = 30
M = N
start = (0, 0)
#end = (N - 1, M - 1)
end = (N // 2, M // 2)
#end = (0, 1)
algo = anti_obstruction
adversary = adversarial_targeted_random

img_number = 0
"""
leniency_iters = 100

def main():
    #random.seed(1)
    #mc_search_score(bfs, N, M, 1000, start, end)
    #return

    L = init_grid_graph(N, M, p=0)

    t0 = time.time()
    #anti_obstruction_buster(L)
    #bfs_buster(L, N, M)
    connect_labyrinth(L)
    t1 = time.time()
    print("Is tree:", nx.is_tree(L))
    print("Is connected:", nx.is_connected(L))
    print("Time, connecting: {0:.3f}s".format(t1 - t0))
    #bfs_buster(L, N, M)
    #return
    num_iter = 100
    #adversarial_targeted_random(algo, L, start, end, num_iter)
    t0 = time.time()
    adversary(algo, L, start, end, num_iter)
    t1 = time.time()
    print("Time, adversary: {0:.3f}".format(t1 - t0))

    #print("End found at depth:", depth)
    #print("Nbr expanded nodes:", num_expanded)
    visualize_labyrinth(algo, L, start, end, show=True, inspection=True)
    #visualize_search(algo, L, start, end)

def visualize_labyrinth(algo, L, start, end, show=False, iteration=0, inspection=False):
    ax.cla()
    draw_labyrinth(ax, L, start, end, N, M)
    T_old = nx.Graph()
    for T in algo(L, start, end, inspection):
        if end not in T:
            T = copy.deepcopy(T)
            #to_be_plotted = set()
            to_be_removed = set()
            for edge in T.edges:
                if edge in T_old.edges:
                    to_be_removed.add(edge)
            #for node in T:
            #    if node not in T_old:
            #        to_be_plotted.add(node)
            T.remove_edges_from(to_be_removed)
            T_old.add_edges_from(T.edges)
            #draw_heuristics(ax, T, to_be_plotted)
            #T.remove_nodes_from(to_be_plotted)

        if algo == anti_obstruction:
            pass
            #from labyrinth.search import Obs
            #draw_obstruction_graph(ax, Obs)
        title = ""
        title = main_draw_search_tree(ax, L, T, start, end)
        title = "Iteration: {}\n".format(iteration) + title

        #ax.set_figsize((6, 4))
        plt.tight_layout()
        plt.subplots_adjust(top=0.8, right=0.9)
        plt.title(title)
        plt.axis("off")
        if show and not inspection:
            plt.show()
        else:
            plt.draw()
            plt.pause(0.001)

        global img_number
        path = os.path.join(gif_dir, "{:03d}".format(img_number))
        plt.savefig(path)
        img_number += 1

if __name__ == '__main__':
    main()