from common.utils import Heap

def bfs_solve(G, start, end):
	expanded_nodes = set()
	h = Heap()
	h.push((0, start))

	while h:
		depth, node = h.pop()
		expanded_nodes.add(node)
		if node == end:
			return depth, expanded_nodes
		for neigh in G[node]:
			if neigh not in expanded_nodes:
				h.push((depth + 1, neigh))

	return None, None