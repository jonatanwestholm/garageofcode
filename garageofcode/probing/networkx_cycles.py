import time
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt

import networkx as nx
from networkx.utils import arbitrary_element
from networkx.algorithms.cycles import simple_cycles

from garageofcode.common import benchmarking
from garageofcode.probing.utils import get_random_graph

def simple_cycles_v001(G):
    def _unblock(thisnode, blocked, B):
        stack = set([thisnode])
        while stack:
            node = stack.pop()
            if node in blocked:
                blocked.remove(node)
                stack.update(B[node])
                B[node].clear()

    # Johnson's algorithm requires some ordering of the nodes.
    # We assign the arbitrary ordering given by the strongly connected comps
    # There is no need to track the ordering as each node removed as processed.
    # Also we save the actual graph so we can mutate it. We only take the
    # edges because we do not want to copy edge and node attributes here.
    subG = type(G)(G.edges())
    sccs = [scc for scc in nx.strongly_connected_components(subG)
            if len(scc) > 1]

    # Johnson's algorithm exclude self cycle edges like (v, v)
    # To be backward compatible, we record those cycles in advance
    # and then remove from subG
    for v in subG:
        if subG.has_edge(v, v):
            yield [v]
            subG.remove_edge(v, v)
    
    while sccs:
        scc = sccs.pop()
        sccG = subG.subgraph(scc)
        # order of scc determines ordering of nodes
        # this sorting provides ~40% speedup
        # prior guess for number of cycles through u
        # is proportional to in_edges * out_edges
        degree = lambda u: len(sccG._pred[u]) * len(sccG._succ[u])
        # minimizing geometric mean of remaining components
        # costs more than it provides...
        #centrality = lambda u: scc_centrality(subG, scc, u)
        #startnode = min(scc, key=centrality)
        startnode = max(scc, key=degree)
        scc.remove(startnode)
        #startnode = scc.pop()
        # Processing node runs "circuit" routine from recursive version
        path = [startnode]
        blocked = set()  # vertex: blocked from search?
        closed = set()   # nodes involved in a cycle
        blocked.add(startnode)
        B = defaultdict(set)  # graph portions that yield no elementary circuit
        stack = [(startnode, list(sccG[startnode]))]  # sccG gives comp nbrs
        while stack:
            thisnode, nbrs = stack[-1]
            if nbrs:
                nextnode = nbrs.pop()
                if nextnode == startnode:
                    yield path[:]
                    closed.update(path)
#                        print "Found a cycle", path, closed
                elif nextnode not in blocked:
                    path.append(nextnode)
                    stack.append((nextnode, list(sccG[nextnode])))
                    closed.discard(nextnode)
                    blocked.add(nextnode)
                    continue
            # done with nextnode... look for more neighbors
            if not nbrs:  # no more nbrs
                if thisnode in closed:
                    _unblock(thisnode, blocked, B)
                else:
                    for nbr in sccG[thisnode]:
                        if thisnode not in B[nbr]:
                            B[nbr].add(thisnode)
                stack.pop()
#                assert path[-1] == thisnode
                path.pop()
        # done processing this node
        H = subG.subgraph(scc)  # make smaller to avoid work in SCC routine
        sccs.extend(scc for scc in nx.strongly_connected_components(H)
                    if len(scc) > 1)


def maximal_strongly_connected_components(G):
    """
    Slower than Tarjan's. Nevermind. 
    """
    while len(G):
        u = arbitrary_element(G)
        decendants = _reachable_from(G, u)
        ancestors = _reachable_from(G._pred, u)
        scc = decendants & ancestors
        yield scc
        if len(scc) > 1:
            print(scc)
        G = G.subgraph(set(G) - scc)


def _reachable_from(G, u):
    visited = set([u])
    stack = [u]
    unvisited = len(G) - 1
    while stack:
        node = stack.pop()
        for v in G[node]:
            if not v in visited:
                visited.add(v)
                stack.append(v)
                unvisited -= 1
                if not unvisited:
                    return visited
    return visited


def test_cycle_speed():
    np.random.seed(0)

    def len_iterator(func):
        return lambda G: sum(1 for _ in func(G))

    nx_iterative = len_iterator(simple_cycles)
    custom1      = len_iterator(simple_cycles_v001)

    funcs = {
             "networkx": nx_iterative,
             "v001": custom1,
             }

    t0 = time.time()
    params = {
              #"star(3)": [star_graph(4)],
              "n=1e1, m=1e1": [get_random_graph(10, 0.1, directed=True)],
              "n=1e2, m=1e2": [get_random_graph(100, 0.01, directed=True)],
              "n=1e2, m=1.7e2": [get_random_graph(100, 0.017, directed=True)],
              #"n=1e3, m=1.4e3": [get_random_graph(1000, 0.0014, directed=True)],
              "n=1e3, m=1e3": [get_random_graph(1000, 0.0026, directed=True)],
              #"n=1e3, m=1e5": [get_random_graph(1000, 0.1, directed=True)],
              #"n=1e3, m=2e5": [get_random_graph(1000, 0.2)],
              #"caveman(100,10)": [connected_caveman_graph(100, 10)],
              #"windmill(10, 10)": [windmill_graph(10, 10)],
              #"nary_tree(3, 1000)": [full_rary_tree(2, 1000)],
              #"complete(20)": [complete_graph(20)],
              }
    t1 = time.time()
    #print("graph generation time: {0:.3f}".format(t1 - t0))

    benchmarking.run(funcs, params)


if __name__ == '__main__':
    test_cycle_speed()