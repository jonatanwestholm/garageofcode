from itertools import product
import numpy as np
from scipy import linalg
import matplotlib.pyplot as plt

from garageofcode.mip.solver import get_solver, status2str
from garageofcode.sampling.timeseries import get_ts

tol = 1e-4

def draw_planes(ax, planes):
    t = np.linspace(-10, 10)
    eps = 0.05

    for plane in planes:
        a, b, d = plane
        assert abs(a + b) > tol
        x = -d/(a + b) + b*t
        y = -d/(a + b) - a*t
        ax.plot(x, y, color='b')
        x_p = x + np.sign(a) * eps
        y_p = y + np.sign(b) * eps
        ax.plot(x_p, y_p, color='r')


def in_hull(u, V):
    """
    Checks if u is in convex hull of V using linear programming.
    V is a list of points
    u is a point
    """

    solver = get_solver("CBC")
    
    X = [solver.NumVar(lb=0) for _ in range(len(V))]
    
    for V_i, u_i in zip(zip(*V), u):
        solver.Add(solver.Dot(V_i, X) == u_i)

    solver.Add(solver.Sum(X) == 1)

    result = solver.Solve(time_limit=10)
    result = status2str[result]
    return result == "OPTIMAL"


def is_inside(point, planes):
    A, d = planes[:, :-1], planes[:, -1]
    proj = np.matmul(A, point) + d
    return np.all(proj >= 0)


def make_plane(points, ref):
    """
    Make a plane with a normal that is orthogonal 
    to all (u - v) where u and v are in points
    The plane intersects all points
    The plane is oriented such that the point
    ref will have a positive value
    """

    p0 = points[0]
    A = np.matrix([p_i - p0 for p_i in points[1:]])
    normal = linalg.null_space(A)
    d = -np.dot(p0, normal)
    sgn = np.dot(ref, normal) + d
    normal *= sgn
    d *= sgn

    plane = np.concatenate([normal.T[0], d])
    return plane


def is_bounded(planes):
    R = 1000
    tol = 1e-6

    if not len(planes):
        return False

    solver = get_solver("CBC")

    X = [solver.NumVar(lb=-R, ub=R) for _ in range(len(planes[0]) - 1)]

    obj = 0
    for A in planes:
        #print(A)
        a, d = A[:-1], A[-1]
        proj = solver.Dot(a, X)
        obj += proj * np.random.random()
        solver.Add(proj >= -d)

    #solver.Add(X[0] <= 1)
    #solver.Add(X[0] >= -1)

    #obj = solver.Dot(np.sum(planes[:, :-1], axis=0), X)

    solver.SetObjective(obj, maximize=True)
    result = solver.Solve(time_limit=10)
    result = status2str[result]
    if result == "INFEASIBLE":
        print("Infeasible!")
        return True
    else:
        sol = [solver.solution_value(x) for x in X]
        print(sol)
        if any([np.abs(y - R) < tol for y in sol]):
            print("Unbounded")
        else:
            print("Bounded")
    print()


def volume(V, n_iter=100):
    """
    Monte Carlo estimate of volume of 
    convex hull of V, intersected with the unit cube
    """

    dim = len(V[0])
    included = []

    num_in = 0
    for _ in range(n_iter):
        x = np.random.random(dim) - 0.5
        incl = in_hull(x, V)
        num_in += incl
        included.append(incl)
    return num_in / n_iter, included


def k_fold_inclusion(V):
    """
    Checks if v_i in ConvHull(V-v_i) for v_i in V
    """

    if len(V) == 0: 
        return 0

    included = []
    num_in = 0
    for i, v_i in enumerate(V):
        incl = in_hull(v_i, [v for j, v in enumerate(V) if j != i])
        num_in += incl
        included.append(incl)
    return num_in / len(V), included


def get_time_correlated_points(dim, N):
    X = get_ts(N+dim-1, p=dim)
    return np.array([X[i:i+dim] for i in range(N)])


def get_correlated_points(dim, N, alpha=0.1):
    A = np.random.random([dim, dim])-0.5
    #Q, _ = np.linalg.qr(A)
    #D = np.diag(10 * np.random.random([dim]))
    #B = np.matmul(np.matmul(Q.T, D), Q)
    #I = np.eye(dim)
    #V = (1 - alpha) * I + alpha * B
    #C = np.linalg.cholesky(V)
    #for row in C:
    #    print([float("{0:.3f}".format(c)) for c in row])

    #e = np.random.randn(dim, N)
    e = np.random.random([dim, N]) - 0.5
    X = np.dot(A, e).T
    return X


def main():
    '''
    for _ in range(1000):
        A = np.random.random([5, 3]) - 0.5
        #A = np.array([[1, -1],
        #              [-1, -1]])

        #print(A)
        is_bounded(A)
    '''

    #points = [[0, 0], [10, 0], [0, 10]]
    avg = 0
    dim = 2
    num_points = 200
    n_iter = 1
    for _ in range(n_iter):
        points = np.random.random([num_points, dim]) - 0.5
        #points = get_correlated_points(dim, num_points, alpha=1)
        x, y = zip(*points)
        vol, included = k_fold_inclusion(points)
        col = ['b' if incl else 'r' for incl in included]
        plt.scatter(x, y, color=col)
        plt.title("K-fold inclusion: {0:.3f}".format(vol))
        plt.show()
        #exit(0)
        print("Volume:", vol)
        avg += vol
    avg = avg / n_iter
    print("Dim={1:d}, Num_points={2:d}, Total avg: {0:.3f}" \
          .format(avg, dim, num_points))

    '''
    fig, ax = plt.subplots()

    for x, y in product(range(-10, 12), repeat=2):
        col = 'r' if in_hull([x, y], points) else 'b'
        ax.scatter(x, y, color=col)

    x, y = zip(*points)
    ax.scatter(x, y, color='g')

    #ax.set_title("Convex hull for S = {(0, 0), (10, 0), (0, 10)}, in red")

    plt.show()
    '''

    '''
    points = np.random.random([10, 2])*10 - 5

    c0 = np.random.choice(len(points), 3, replace=False)
    c = [points[ch] for ch in c0]

    plane1 = make_plane([c[0], c[1]], c[2])
    plane2 = make_plane([c[0], c[2]], c[1])
    plane3 = make_plane([c[1], c[2]], c[0])

    planes = np.array([plane1, plane2, plane3])

    fig, ax = plt.subplots()

    for x, y in product(np.linspace(-10, 10, 20), repeat=2):
        col = 'r' if is_inside([x, y], planes) else 'b'
        ax.scatter(x, y, color=col)

    draw_planes(ax, planes)

    plt.show()
    '''

    #planes = np.random.random([3, 3]) - 0.5
    #point = np.array([[0], [0]])

    #points = np.array([[1, 0], [0, 1]])
    #ref = [0, 0]

    #make_plane(points, ref)

    '''
    '''

    #for _ in range(100):
    #    print("is inside:", is_inside(point, planes))


if __name__ == '__main__':
    main()