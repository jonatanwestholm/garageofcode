import numpy as np

import networkx as nx

from sentian_miami import get_solver
from garageofcode.networkx.utils import get_random_graph

def get_xkcd730_graph():
    G = nx.DiGraph()
    edges = [(0, 1), (0, 7), (0, 9), (0, 10),
             (1, 7), (1, 3), (1, 6),
             (3, 4), (3, 5),
             (4, 5), (4, 9),
             (5, 8),
             (6, 7), (6, 8),
             (7, 8), (7, 9), (7, 12), (7, 13), (7, 14),
             (8, 14),
             (9, 10), (9, 11),
             (10, 11),
             (11, 12), (11, 13),
             (12, 13),
             (13, 14)
             ]

    G.add_edges_from(edges)
    return G


def get_flows(G, s, t, capacity):
    solver = get_solver("CBC")

    flows = {(u, v): solver.NumVar(lb=0, ub=cap) for u, v, cap in G.edges(data=capacity)}

    for node in G:
        in_flow = solver.Sum([flows[e] for e in G.in_edges(node)])
        out_flow = solver.Sum([flows[e] for e in G.out_edges(node)])

        if node == s:
            total_in = out_flow - in_flow
        elif node == t:
            total_out = in_flow - out_flow
        else:
            solver.Add(in_flow == out_flow)

    solver.SetObjective(total_out, maximize=True)

    solver.Solve(time_limit=10, verbose=True)
    total_out = solver.solution_value(total_out)
    #print("Total out:", total_out)
    return {e: solver.solution_value(flow) for e, flow in flows.items()}


def main():
    np.random.seed(1)
    #G = get_xkcd730_graph()
    G = get_random_graph(100, 0.2, directed=True)
    get_flows(G, 0, max(G))


if __name__ == '__main__':
    main()