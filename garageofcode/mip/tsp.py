import numpy as np

from garageofcode.mip.solver import get_solver

def tsp(points, depot=None):
    """MIP exact solution of TSP
    Returns the edges
    """
    if not points:
        return []
    if depot is None:
        depot = points[0]
    else:
        points = [depot] + points
    # set entrance and exit depot the same
    points.append(depot)
    ids, coords = zip(*points)
    N = len(ids)

    solver = get_solver("CBC")
    D  = np.array([[np.linalg.norm(x - y) 
                    for y in coords] for x in coords])
    #  gate variables
    GV = np.array([[solver.IntVar(0, int(i != j)) 
                    for j in range(N)] for i in range(N)])
    #  time variables
    TV = [solver.NumVar(lb=0) for _ in range(N)]
    
    #  exactly one entrance to all except entrance depot
    for j in range(1, N):
        solver.Add(solver.Sum(GV[:, j]) == 1)
    #  no entrance to entrance depot
    solver.Add(solver.Sum(GV[:, 0]) == 0)

    #  exactly one exit from all except exit depot
    for i in range(N-1):
        solver.Add(solver.Sum(GV[i, :]) == 1)
    #  no exit from exit depot
    solver.Add(solver.Sum(GV[-1, :]) == 0)

    #  can get tighter big M, by greedy solution
    #  actually, it doesn't make it faster
    M = N * np.max(D) * 2
    #  eliminate subtours with time variable formulation
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            gv = GV[i, j]
            d = D[i, j]
            solver.Add(TV[j] >= TV[i] + d - M * (1 - gv))

    #  minimize finish time
    solver.SetObjective(TV[-1], maximize=False)

    solver.Solve(time_limit=10, verbose=False)

    idx_order = np.argsort([solver.solution_value(tv) for tv in TV])
    return [(ids[idx0], ids[idx1]) 
                for idx0, idx1 in zip(idx_order, idx_order[1:])]


    '''
    sample = partial(np.random.choice, size=k, replace=False)
    c = Counter(chain.from_iterable(tsp([points[i] 
                            for i in sample(n)]) for _ in range(num_iter)))


    for (u, v), num in c.items():
        u = points[u][1]
        v = points[v][1]
        x, y = zip(*[u, v])
        plt.plot(x, y, linewidth=num, color='b')
    plt.show()
    '''

    '''
    #  solution synthesis
    #  this is super stupid
    G = nx.Graph()
    for i in range(n):
        G.add_node(i)
    def unsaturated(u):
        return len(G[u]) <= 1
    for (u, v), _ in c.most_common():
        if unsaturated(u) and unsaturated(v):
            try:
                nx.shortest_path_length(G, u, v)
            except nx.exception.NetworkXNoPath:
                G.add_edge(u, v)

    for u, v in G.edges():
        u = points[u][1]
        v = points[v][1]
        x, y = zip(*[u, v])
        plt.plot(x, y, color='b')
    plt.show()
    '''

