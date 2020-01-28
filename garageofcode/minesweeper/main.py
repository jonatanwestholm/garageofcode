from itertools import product

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backend_bases import MouseButton

import networkx as nx

adj2col = {"0": "0.25", "1": "b", "2": "g", "3": "r",
           "4": "y", "5": "c", "6": "m", "7": "m", "8": "m",
           "*": "k", "N": "0.75"}

fig, ax = plt.subplots()

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

class Board(nx.Graph):
    def __init__(self, N, M, S):
        super().__init__()
        self.N = N
        self.M = M
        self.S = S
        # init the grid
        G = grid_8connect(N, M)
        self.add_edges_from(G.edges)
        for node in self:
            self.nodes[node]["mine"] = None
            self.nodes[node]["adj"]  = None

    def populate(self):
        for node in self:
            self.nodes[node]["mine"] = 0
        
        # add the mines
        locs = list(product(range(self.N), range(self.M)))
        mines = np.random.choice(self.N*self.M, self.S, replace=False)
        mines = [locs[idx] for idx in mines]
        for mine in mines:
            self.nodes[mine]["mine"] = 1

        # count neighbouring mines
        for node in self:
            adjacent_mines = sum([self.nodes[neigh]["mine"] 
                                    for neigh in self[node]])
            self.nodes[node]["adj"] = adjacent_mines

    def open(self, node):
        if self.nodes[node]["mine"]:
            print("We opened a mine!", node)
            return None
        else:
            return self.nodes[node]["adj"]

    def update(self, node, adj):
        if adj is None:
            self.nodes[node]["mine"] = 1
        else:
            self.nodes[node]["mine"] = 0
            self.nodes[node]["adj"]  = adj

    def sweep(self, board, node):
        adj = board.open(node)
        self.update(node, adj)

    def flag(self, node):
        self.nodes[node]["mine"] = 1

    def get_0(self):
        node_0s = [node for node in self
                    if self.nodes[node]["adj"] == 0 and not self.nodes[node]["mine"]]
        return node_0s[np.random.randint(0, len(node_0s))]        

    def num_unknown_neigh(self, node):
        return sum([self.nodes[neigh]["mine"] is None for neigh in self[node]])

    def num_mine_neigh(self, node):
        return sum([self.nodes[neigh]["mine"] == 1 for neigh in self[node]])

    def exhaust_0(self, board, node_0):
        # given a node with 0 adjacent mines,
        # open all adjacents,
        # and do this recursively

        queue = [node_0]
        while queue:
            node = queue.pop()
            for neigh in self[node]:
                if self.nodes[neigh]["adj"] is None:
                    adj = board.open(neigh)
                    self.update(neigh, adj)
                    if adj == 0:
                        queue.append(neigh)

    def exhaust_1(self, board):
        while True:
            for node in self.nodes:
                if self.nodes[node]["adj"] is None:
                    continue

                if not self.num_unknown_neigh(node):
                    continue

                if self.nodes[node]["adj"] == self.num_mine_neigh(node) + self.num_unknown_neigh(node):
                    # All remaining adjacent tiles are mines
                    for neigh in self[node]:
                        if self.nodes[neigh]["mine"] is None:
                            #print("mine:", node, "-->", neigh)
                            self.update(neigh, None)
                    break

                if self.nodes[node]["adj"] == self.num_mine_neigh(node):
                    # We have found all adjacent mines
                    for neigh in self[node]:
                        if self.nodes[neigh]["mine"] is None:
                            adj = board.open(neigh)
                            self.update(neigh, adj)
                            if adj is None:
                                return
                    break

            else:
                break


    def plot(self, fig=None, ax=None):
        if fig is None:
            fig, ax = plt.subplots()

        for i in range(self.N + 1):
            ax.axhline(i, color="k")

        for i in range(self.M + 1):
            ax.axvline(i, color="k")

        ax.set_xlim(0, self.M)
        ax.set_ylim(0, self.N)

        for i in range(self.N):
            for j in range(self.M):
                mine = self.nodes[(i, j)]["mine"]
                adj = self.nodes[(i, j)]["adj"]
                if mine:
                    s = "*"
                elif adj is not None:
                    s = str(adj)
                else:
                    s = "N"
                ax.text(j+0.4, i+0.3, s, color=adj2col[s], fontweight="bold")

        patch = Rectangle((0, 0), self.M, self.N, facecolor=adj2col["N"])
        ax.add_patch(patch)
        return fig, ax

def onclick(event):
    i = event.ydata
    j = event.xdata
    if i is None or not (0 <= i <= solution.N):
        return
    if j is None or not (0 <= j <= solution.M):
        return 
    node = (int(i), int(j))
    button = event.button

    if button == MouseButton.LEFT:
        solution.sweep(board, node)
        print("sweeped:", solution.nodes[node]["adj"])
    elif button == MouseButton.RIGHT:
        solution.flag(node)
        #print(solution.nodes[node]["mine"])
        print("flagged")

    solution.exhaust_1(board)

    plt.cla()
    solution.plot(fig, ax)
    plt.draw()

def main():
    #np.random.seed(0)

    N = 16 # height
    M = 30 # width
    S = 99 # number of mines

    global board
    board = Board(N, M, S)
    board.populate()
    global solution
    solution = Board(N, M, S)
    node_0 = board.get_0()

    #fig_board, ax_board = board.plot()
    #ax_board.set_title("Ground Truth")

    solution.exhaust_0(board, node_0)
    #ax = solution.plot()
    #ax.set_title("Exhaust 0")

    solution.exhaust_1(board)
    solution.plot(fig, ax)
    #ax.set_title("Exhaust 1")


    fig.canvas.mpl_connect('button_press_event', onclick)

    plt.show()

if __name__ == '__main__':
    main()