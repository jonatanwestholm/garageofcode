from itertools import product

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import networkx as nx

adj2col = {"0": "0.75", "1": "b", "2": "g", "3": "r",
           "4": "y", "5": "c", "6": "m", "7": "m", "8": "m",
           "*": "k", "N": "w"}

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
        self.N = N
        self.M = M
        self.S = S
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
        node_0s = [node for node in self.G 
                    if self.G.nodes[node]["adj"] == 0 and not self.G.nodes[node]["mine"]]
        return node_0s[np.random.randint(0, len(node_0s))]

    def plot(self):
        fig, ax = plt.subplots()

        for i in range(self.N + 1):
            ax.axhline(i, color="k")

        for i in range(self.M + 1):
            ax.axvline(i, color="k")


        ax.set_xlim(0, self.N)
        ax.set_ylim(0, self.M)

        for i in range(self.N):
            for j in range(self.M):
                adj = self.open((i, j))
                adj = str(adj) if adj is not None else "*"
                ax.text(j+0.4, i+0.3, adj, color=adj2col[adj], fontweight="bold")

        patch = Rectangle((0, 0), self.M, self.N, facecolor=adj2col["0"])
        ax.add_patch(patch)


class Solution:
    def __init__(self, N, M, S):
        self.N = N
        self.M = M
        self.S = S
        self.G = grid_8connect(N, M)
        for node in self.G:
            self.G.nodes[node]["mine"] = None
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
                        queue.append(neigh)

    def exhaust_1(self, board):
        unchecked = self.G.nodes
        while True:
            opened = []
            for node in unchecked:
                if self.adj(node) is None:
                    continue

                if not self.num_unknown_neigh(node):
                    continue

                if self.adj(node) == self.num_mine_neigh(node):
                    for neigh in self.G[node]:
                        if self.mine(neigh) is None:
                            pass # fuck. need to find a better representation of unknown
                        adj = board.open(node)
                        if adj is None:
                            print("We hit a mine!")
                        self.update(node, adj)




            if opened:
                unchecked = opened
            else:
                break

    def adj(self, node):
        return self.G.nodes[node]["adj"]

    def mine(self, node):
        return self.G.nodes[node]["mine"]        

    def num_unknown_neigh(self, node):
        return sum([self.adj(node) is None for neigh in self.G[node]])

    def num_mine_neigh(self, node):
        return sum([self.mine(node) == 1 for neigh in self.G[node]])

    def open(self, node):
        if self.mine(node):
            return "*"
        else:
            return self.adj(node)

    def plot(self):
        fig, ax = plt.subplots()

        for i in range(self.N + 1):
            ax.axhline(i, color="k")

        for i in range(self.M + 1):
            ax.axvline(i, color="k")

        ax.set_xlim(0, self.N)
        ax.set_ylim(0, self.M)

        for i in range(self.N):
            for j in range(self.M):
                adj = self.open((i, j))
                adj = str(adj) if adj is not None else "N"
                ax.text(j+0.4, i+0.3, adj, color=adj2col[adj], fontweight="bold")

        patch = Rectangle((0, 0), self.M, self.N, facecolor=adj2col["0"])
        ax.add_patch(patch)


def main():
    N = 10 # height
    M = 10 # width
    S = 10 # number of mines

    board = Board(N, M, S)
    solution = Solution(N, M, S)
    node_0 = board.get_0()
    print(node_0)
    solution.exhaust_0(board, node_0)

    board.plot()
    solution.plot()

    plt.show()


if __name__ == '__main__':
    main()