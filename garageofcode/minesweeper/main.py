import time
from itertools import product, chain

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backend_bases import MouseButton

import networkx as nx

adj2col = {"0": "0.5", "1": "b", "2": "g", "3": "r",
           "4": np.array([1, 1, 0.5]), "5": "c", "6": "m", "7": "m", "8": "m",
           "-1": "r", "-2": "r", "-3": "r", "-4": "r", 
           "-5": "r", "-6": "r", "-7": "r", "-8": "r",
           "*": "k", "N": "0.75"}

fig, ax = plt.subplots()
t0 = time.time()

def flatten(lst):
    return [elem for sublist in lst for elem in sublist]

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
    return G

class Board(nx.Graph):
    def __init__(self, N, M, S):
        super().__init__()
        self.N = N
        self.M = M
        self.S = S
        self.use_sat = False
        # init the grid
        G = grid_8connect(N, M)
        self.add_edges_from(G.edges)
        for node in self:
            self.nodes[node]["mine"] = None
            self.nodes[node]["adj"]  = None

    def import_sat(self):
        global SugarRush
        from sugarrush.solver import SugarRush

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

    def get_unknown_neigh(self, node):
        return [neigh for neigh in self[node] if self.nodes[neigh]["mine"] is None]

    def num_unknown_neigh(self, node):
        return len(self.get_unknown_neigh(node))

    def num_mine_neigh(self, node):
        return sum([self.nodes[neigh]["mine"] == 1 for neigh in self[node]])

    def num_mines_total(self):
        return sum([self.nodes[node]["mine"] == 1 for node in self])

    def num_opened_total(self):
        return sum([self.nodes[node]["adj"] is not None for node in self])

    def is_done(self):
        return self.num_opened_total() == self.N * self.M - self.S

    def exhaust_0(self, board, node_0):
        # given a node with 0 adjacent mines,
        # open all adjacents,
        # and do this recursively
        adj = board.open(node_0)
        self.update(node_0, adj)

        queue = [node_0]
        while queue:
            node = queue.pop()
            for neigh in self[node]:
                if self.nodes[neigh]["adj"] is None:
                    adj = board.open(neigh)
                    self.update(neigh, adj)
                    if adj == 0:
                        queue.append(neigh)

    def exhaust_1(self, board, center=None):
        while True:
            for node in self.nodes:
                if self.nodes[node]["adj"] is None:
                    continue

                if not self.num_unknown_neigh(node):
                    continue

                if self.nodes[node]["adj"] == self.num_mine_neigh(node) \
                                              + self.num_unknown_neigh(node):
                    # All remaining adjacent tiles are mines
                    for neigh in self[node]:
                        if self.nodes[neigh]["mine"] is None:
                            #print("mine:", node, "-->", neigh)
                            self.update(neigh, None)
                    if center is not None:
                        nodes.update(list(self[node]))
                        nodes.update(flatten([self[nd] for nd in self[node]]))
                    break

                if self.nodes[node]["adj"] == self.num_mine_neigh(node):
                    # We have found all adjacent mines
                    for neigh in self[node]:
                        if self.nodes[neigh]["mine"] is None:
                            adj = board.open(neigh)
                            self.update(neigh, adj)
                            if adj is None:
                                return
                    if center is not None:
                        nodes.update(list(self[node]))
                        nodes.update(flatten([self[nd] for nd in self[node]]))
                    break

            else:
                break

    def exhaust_inf(self, board):
        if not self.use_sat:
            self.use_sat = True
            self.import_sat()

        while True:
            self.exhaust_1(board)

            # build SAT model
            # node2var dict
            # find known tiles (opened + flagged)
            # dilute once, reduce original, remaining is border
            # one SAT var for each tile on border
            # one cardinality constraint per opened tile adjacent to border
            # loop through SAT vars
            # for each var, try assumption that var = 0, then var = 1
            # if either assumption fails to be satisfiable, we are certain of the other
            # when finding a certainty, open/flag, then jump to loop again
            # else: break

            solver = SugarRush()
            
            known_tiles = set([node for node in self if self.nodes[node]["mine"] is not None])
            known_dilute = set(flatten([self[node] for node in known_tiles]))
            rim = known_dilute - known_tiles

            unknown_tiles = set(self.nodes) - known_tiles
            unknown_dilute = set(flatten([self[node] for node in unknown_tiles]))
            front = unknown_dilute - unknown_tiles

            node2var = {node: solver.var() for node in rim}
            
            # cardinality constraints
            for node in front:
                if self.nodes[node]["adj"] is None: # mine
                    continue

                unknown_neigh = self.get_unknown_neigh(node)
                unknown_neigh = [node2var[neigh] for neigh in unknown_neigh]
                adj = self.nodes[node]["adj"]
                flagged_neigh = self.num_mine_neigh(node)
                remaining_mines = adj - flagged_neigh
                solver.add(solver.equals(unknown_neigh, bound=remaining_mines))

            # global constraint
            all_vars = [var for var in node2var.values()]
            remaining_mines = self.S - self.num_mines_total()
            if len(rim) == len(unknown_tiles):
                solver.add(solver.equals(all_vars, bound=remaining_mines))
            else:
                solver.add(solver.atmost(all_vars, bound=remaining_mines))

            for node in rim:
                var = node2var[node]
                if not solver.solve(assumptions=[var]): 
                    # assumption that it's a mine failed -
                    # must be free
                    self.sweep(board, node)
                    break
                if not solver.solve(assumptions=[-var]):
                    # assumption that it's free failed - 
                    # must be a mine
                    self.flag(node)
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
                node = (i, j)
                mine = self.nodes[node]["mine"]
                adj = self.nodes[node]["adj"]
                if mine:
                    s = "*"
                elif adj is not None:
                    #s = str(adj)
                    rem = adj - self.num_mine_neigh(node)
                    s = str(rem)
                else:
                    s = "N"
                ax.text(j+0.4, i+0.3, s, color=adj2col[s], fontweight="bold")

        patch = Rectangle((0, 0), self.M, self.N, facecolor=adj2col["N"])
        ax.add_patch(patch)
        return fig, ax


def get_workable(N, M, S):
    i = 0
    while True:
        board = Board(N, M, S)
        board.populate()
        solution = Board(N, M, S)
        node_0 = board.get_0()
        solution.exhaust_0(board, node_0)
        solution.exhaust_inf(board)
        if solution.is_done():
            return board, node_0
        else:
            print("unworkable", i)
        i += 1


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
        print("swept:", solution.nodes[node]["adj"])
    elif button == MouseButton.RIGHT:
        solution.flag(node)
        #print(solution.nodes[node]["mine"])
        print("flagged")
    elif button == MouseButton.MIDDLE:
        # run SAT
        solution.exhaust_inf(board)
        print("ran exhaust_inf")

    solution.exhaust_1(board)

    plt.cla()
    solution.plot(fig, ax)
    ax.set_title("Mines: {0:d}/{1:d}".format(solution.num_mines_total(), solution.S))
    plt.draw()

    if solution.is_done():
        print("Done!")
        print("Time: {0:.1f}s".format(time.time() - t0))

def main():
    np.random.seed(0)
    # good expert: 52, 56 (global), 58 (tricky), 
    #  64 (corridor), 68 (two moves), 72 (tricky extension), 
    #  74 (long), 75 (global), 78 (trivially solved!), 79
    #  89 (simple opening), 90 (hard beginning), 92 (good tiledom),
    #  
    level = 300

    if level == 1: # beginner
        N, M, S = 8, 8, 10
    elif level == 2: # intermediate
        N, M, S = 16, 16, 40
    elif level == 2.5: # between intermediate and expert
        N, M, S = 15, 25, 72
    elif level == 3: # expert
        N, M, S = 16, 30, 99
    elif level == 4: # expert plus
        N, M, S = 16, 30, 108
    else: 
        # "The 300"
        N, M, S = 30, 50, 325

    #N = 16 # height
    #M = 16 # width
    #S = 40 # number of mines

    global board
    board, node_0 = get_workable(N, M, S)
    #board = Board(N, M, S)
    #board.populate()
    global solution
    solution = Board(N, M, S)
    #node_0 = board.get_0()

    #fig_board, ax_board = board.plot()
    #ax_board.set_title("Ground Truth")

    solution.exhaust_0(board, node_0)
    #ax = solution.plot()
    #ax.set_title("Exhaust 0")

    solution.exhaust_1(board)
    solution.plot(fig, ax)
    ax.set_title("Mines: {0:d}/{1:d}".format(solution.num_mines_total(), solution.S))
    #ax.set_title("Exhaust 1")
    if solution.is_done():
        print("Done!")
        print("Time: {0:.1f}s".format(time.time() - t0))

    fig.canvas.mpl_connect('button_press_event', onclick)

    plt.show()

if __name__ == '__main__':
    main()