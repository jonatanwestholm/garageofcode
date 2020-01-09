from itertools import product

import numpy as np

import networkx as nx

def grid_8connect(N, M):
    G = nx.Graph()
    for n in range(N):
        for m in range(M):
            if n < N - 1:
                G.add_edge((n, m), (n + 1, m))
            if m < M - 1:
                G.add_edge((n, m), (n, m + 1))
            if n < N - 1 and m < M - 1:
                G.add_edge((n, m), (n + 1, m + 1))
            if n < N - 1 and m > 0:
                G.add_edge((n, m), (n + 1, m - 1))

    #A = np.zeros([N, M])
    #for n in range(N):
    #    for m in range(M):
    #        A[n, m] = len(G[(n, m)])
    #print(A)
    #exit(0)
    return G

class Board:
    def __init__(self, N, M, S):
        # init the grid
        self.G = grid_8connect(N, M)
        for node in self.G:
            self.G.nodes[node]["mine"] = 0
        
        # add the mines
        locs = list(product(range(N), range(M)))
        mines = np.random.choice(N*M, S, replace=False)
        mines = [locs[idx] for idx in mines]
        for mine in mines:
            self.G.nodes[mine]["mine"] = 1

        # count neighbouring mines
        for node in self.G:
            adjacent_mines = sum([self.G.nodes[neigh]["mine"] 
                                    for neigh in self.G[node]])
            self.G.nodes[node]["adj"] = adjacent_mines

    def open(self, node):
        if self.G.nodes[node]["mine"]:
            return None
        else:
            return self.G.nodes[node]["adj"]

    def get_0(self):
        return np.random.choice([node for node in self.G 
                                    if self.G.nodes[node]["adj"] == 0])

class Solution:
    def __init__(self, N, M, S):
        self.G = grid_8connect(N, M)
        for node in self.G:
            #self.G.nodes[node]["mine"] = None
            self.G.nodes[node]["adj"] = None

    def update(self, node, adj):
        self.G.nodes[node]["adj"] = adj

    def exhaust_0(self, board, node_0):
        # given a node with 0 adjacent mines,
        # open all adjacents,
        # and do this recursively

        queue = [node_0]
        while queue:
            node = queue.pop()
            for neigh in self.G[node]:
                if self.G.nodes[neigh]["adj"] is None:
                    adj = board.open(neigh)
                    self.update(neigh, adj)
                    if adj == 0:
                        queue.append(adj)


def main():
    N = 10 # height
    M = 10 # width
    S = 10 # number of mines

    Board(N, M, S)


if __name__ == '__main__':
    main()