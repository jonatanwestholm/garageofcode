import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from itertools import product, groupby
import networkx as nx

from solver import get_solver

def get_graph():
	G = nx.Graph()

	for ch in "ABCDEFGH":
		G.add_node(ch, level="top")
		for i in range(4):
			G.add_node((ch, i), level="sub")

	G.add_edge("A", "C", sides=(2, 0))
	G.add_edge("B", "C", sides=(1, 3))
	G.add_edge("D", "C", sides=(3, 1))
	G.add_edge("G", "C", sides=(0, 2))

	G.add_edge("B", "F", sides=(2, 0))
	G.add_edge("E", "F", sides=(1, 3))
	G.add_edge("G", "F", sides=(3, 1))
	G.add_edge("H", "F", sides=(0, 2))

	for u, v, data in G.edges(data=True):
		data["level"] = "top"

	for u, v, (i, j) in G.edges(data="sides"):
		G.add_edge((u, i), (v, (j + 1)%4), level="sub")
		G.add_edge((u, (i + 1)%4, (v, j)), level="sub")

	return G


def bind_to_structure(solver, G, X, Y):
	pass


def main():
	G = get_graph()
	N = 8
	locs = "ABCDEFGH"
	tiles = list(range(8))
	turns = list(range(4))
	dots = list(range(4))
	cols = list(range(4))

	solver = get_solver("CBC")

	X = {(loc, tile, turn): solver.IntVar(0, 1) 
			for loc, tile, turn in product(locs, tiles, turns)}

	# Constraint: exactly one tile with one turn per location
	for isolocs in groupby(X.items(), key=lambda x: x[0][0]):
		_, isolocs = zip(*isolocs)
		solver.Add(solver.Sum(isolocs) == 1)

	# Constraint: tile must be placed in exactly one tile with one turn
	for isotile in groupby(X.items(), key=lambda x: (x[0][1], x[0][2])):
		_, isotile = zip(*isotile)
		solver.Add(solver.Sum(isotile) == 1)

	# auxilliary variables
	Y = {(loc, dot, col): solver.IntVar(0, 1) 
			for loc, dot, col in product(locs, dots, cols)}

	for isolocs in groupby(Y.items(), key=lambda x: x[0][0]):
		for isodots in groupby(isolocs, key=lambda x: x[0][1]):
			_, isodots = zip(*isodots)
			solver.Add(solver.Sum(isodots) == 1)

		for isocols in groupby(isolocs, key=lambda x: x[0][2]):
			_, isocols = zip(*isocols)
			solver.Add(solver.Sum(isocols) == 1)

	bind_to_structure(solver, G, X, Y)

	solver.Solve(time_limit=10)

	# presentation

if __name__ == '__main__':
	main()