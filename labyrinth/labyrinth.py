import time
import random
import matplotlib.pyplot as plt
import networkx as nx

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

def main():
    random.seed(0)
    N = 9
    start = (0, 0)
    end = (N-1, N-1)
    L = init_grid_graph(N, N, p=0)

    #connect_labyrinth(L)
    node_expansion_buster(L, N, N)
    
    nodes = nx.shortest_path(L, start, end)

    fig, ax = plt.subplots()

    draw_labyrinth(ax, L, N, N)
    draw_path(ax, nodes)

    plt.axis("off")
    plt.show()
    

if __name__ == '__main__':
    main()