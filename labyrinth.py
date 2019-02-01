import random
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import networkx as nx

def draw_labyrinth(ax, L, n, m):
	start_tile = Rectangle((0, 0), 1, 1, facecolor='g')
	end_tile = Rectangle((n - 1, m - 1), 1, 1, facecolor='r')

	ax.add_patch(start_tile)
	ax.add_patch(end_tile)

	ax.plot([0, n], [0, 0], 'k')
	ax.plot([0, n], [m, m], 'k')
	ax.plot([0, 0], [0, m], 'k')
	ax.plot([n, n], [0, m], 'k')

	for i in range(n):
		for j in range(m):
			if (i, j + 1) not in L[(i, j)]:
				ax.plot([j + 1, j + 1], [i, i + 1], 'k')
			if (i + 1, j) not in L[(i, j)]:
				ax.plot([j, j + 1], [i + 1, i + 1], 'k')


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

def main():
	N = 30
	L = init_grid_graph(N, N, p=0)

	connect_labyrinth(L)
	
	fig, ax = plt.subplots()

	draw_labyrinth(ax, L, N, N)

	plt.axis("off")
	plt.show()
	

if __name__ == '__main__':
	main()