import networkx as nx
from common.utils import Heap, shuffled

def bfs(G, start, end):
	T = nx.Graph() # the search tree
	expanded_nodes = set()
	heap = Heap()
	heap.push((0, start))

	while heap:
		depth, node = heap.pop()
		#print(node)
		expanded_nodes.add(node)
		if node == end:
			break
		for neigh in G[node]:
			if neigh not in expanded_nodes:
				#print("\t", neigh)
				T.add_edge(node, neigh)
				heap.push((depth + 1, neigh))
			else:
				pass#print("\t", neigh, "v")
	else:
		print("Warning: bfs did not find path from {} to {}".format(start, end))

	#dead_end_nodes = heap._h #set(T.nodes) - expanded_nodes
	#T.remove_nodes_from(dead_end_nodes)
	#print("Start in dead_end_nodes:", start in T)
	#print("End in dead_end_nodes:", end in T)
	#print("END\n\n")
	return T

def dfs(G, start, end):
	T = nx.Graph() # the search tree
	expanded_nodes = set()
	stack = [(0, start)]

	while stack:
		depth, node = stack.pop()
		expanded_nodes.add(node)
		if node == end:
			break
		for neigh in shuffled(G[node]):
			if neigh not in expanded_nodes:
				T.add_edge(node, neigh)
				stack.append((depth + 1, neigh))
	else:
		print("Warning: dfs did not find path from {} to {}".format(start, end))

	dead_end_nodes = set(T.nodes) - expanded_nodes
	T.remove_nodes_from(dead_end_nodes)
	return T
