import random
import matplotlib.pyplot as plt
import networkx as nx

def grid_graph(n, m):
	G = nx.Graph()
	for i in range(n):
		for j in range(m):
			G.add_node((i, j))
			if j < m - 1 and random.random() < 0.5:
				G.add_edge((i, j), (i, j + 1), link = 1)
			if i < n - 1 and random.random() < 0.5:
				G.add_edge((i, j), (i + 1, j), link = 1)

	return G

def draw_labyrinth(ax, L, n, m):
	ax.plot([0, n], [0, 0], 'k')
	ax.plot([0, n], [m, m], 'k')
	ax.plot([0, 0], [0, m], 'k')
	ax.plot([n, n], [0, m], 'k')

	for i in range(n):
		for j in range(m):
			if (i, j + 1) in L[(i, j)] and L[(i, j)][(i, j + 1)]['link']:
				ax.plot([j + 1, j + 1], [i, i + 1], 'k')
			if (i + 1, j) in L[(i, j)] and L[(i, j)][(i + 1, j)]['link']:
				ax.plot([j, j + 1], [i + 1, i + 1], 'k')


def main():
	N = 10
	G = grid_graph(N, N)

	fig, ax = plt.subplots()

	draw_labyrinth(ax, G, N, N)

	plt.show()


if __name__ == '__main__':
	main()