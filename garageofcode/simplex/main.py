import numpy as np

# or-tools convention
status2str = ["OPTIMAL", "FEASIBLE", "INFEASIBLE", "UNBOUNDED", 
              "ABNORMAL", "MODEL_INVALID", "NOT_SOLVED"]

def pivot(T, pc, pr):
    #print("pc:", pc, "pr:", pr)
    pe = T[pr, pc] # pivot element
    pivot_row = T[pr, :] * 1.0 # stupid numpy copy gotcha
    pivot_row /= pe
    offset = np.dot(T[:, pc].reshape([-1, 1]), pivot_row.reshape([1, -1]))
    T -= offset
    T[pr, :] = pivot_row
    return T


def select_pivot_column(z):
    """
    Pick one variable that increases the objective
    """

    for i, zi in enumerate(z):
        if zi > 0:
            return i + 1
    else:
        return None


def select_pivot_row(Tc, b):
    """
    Which ceiling are we going to hit our head in first?
    """

    #print(Tc)
    if all(Tc <= 0): # no roof over our head - to the stars!
        return None

    ratios = [bi / Tci if Tci > 0 else np.inf for Tci, bi in zip(Tc, b)]
    #print("ratios:", ratios)
    return np.argmin(ratios) + 1


def collect_solution(T, basic):
    num_slack = len(basic)
    num_vars = len(T[0]) - num_slack - 2
    b = T[1:, -1]

    solution = np.zeros([num_vars])

    for pr, pc in enumerate(basic):
        if pc <= num_slack: # is a slack variable
            continue

        solution[pc - num_slack - 1] = T[pr + 1, -1] / T[pr + 1, pc]

    return solution


def phase2(A, b, c):
    """
    maximize c * x 
    such that
    Ax <= b
    x >= 0
    b >= 0
    """

    # build a tableau T
    #T = [1 -c 0 0;
    #     0  A I b]
    # where I corresponds to s, slack variables

    # Loop, terminate when no pivot column can be selected

        # select pivot column
        # given pivot column, select pivot row
        # given pivot element, perform pivot operation

    # need to keep track of:
    #   which variables are basic

    # returning the solution: identify basic variables among original variables
    # set nonbasic variables to 0

    num_slack, num_vars = A.shape
    z_s0 = np.zeros([num_slack])
    z_s1 = np.zeros([num_slack, 1])

    T1 = np.hstack([np.array([1]), z_s0, c, np.array([0])])
    T2 = np.hstack([z_s1, np.eye(num_slack), A, b])
    T = np.vstack([T1, T2])

    #print(T)

    basic = list(range(num_slack))

    while True:
        pc = select_pivot_column(T[0, 1:])
        if pc is None: # found optimum
            break
        #print("pc:", pc)

        pr = select_pivot_row(T[1:, pc], T[1:, -1])
        if pr is None: # unbounded
            return None, np.inf
        #print("pr:", pr)

        T = pivot(T, pc, pr)
        #print(T)

        basic[pr - 1] = pc

    return collect_solution(T, basic), -T[0, -1]

def phase1(A, b, c):
    """
    find a feasible solution to 
    Ax <= b
    x >= 0
    """

    num_constr, num_vars = A.shape
    I = np.eye(num_constr)

    c_ext = np.concatenate([np.zeros([num_vars]), -1 * np.ones([num_constr])])
    A_ext = np.hstack([A, -I])
    z_init = -b * (b < 0)
    print("z_init:\n", z_init)
    x_relaxed = np.concatenate([np.zeros([num_vars, 1]), z_init])
    print("x_relaxed:\n", x_relaxed)
    A_prim, b_prim, c_prim, d_prim = phase1_5(A_ext, b, c_ext, x_relaxed)
    #c_prim[-len(c_prim) // 2:] = 0
    print("A_prim:\n", A_prim)
    print("b_prim:\n", b_prim)
    print("c_prim:\n", c_prim)
    print("d_prim:\n", d_prim)

    x_bfs, val = phase2(A_prim, b_prim, c_prim)

    print(x_bfs, val)
    #exit(0)

    tol = 1e-8
    if val > tol + d_prim: # infeasible
        return None

    return x_bfs[:num_vars]

def phase1_5(A, b, c, x_bfs):
    """
    Given a basic feasible solution x_bfs,
    perform variable substitution so that
    
    A'x' <= b'
    x' >= 0
    b' >= 0.

    Also transform c to c' and add constant d, 
    to preserve optimum.

    A' = [A, -A;
          0, I]
    b' = [b - A*x_bfs;
          x_bfs]
    c' = [c, -c]
    d = c*x_bfs.

    Effectively what we're doing is renaming

    x = x_positive - x_negative + x_bfs
    x_positive, x_negative >= 0
    where 
    x >= 0  ->  x_positive - x_negative + x_bfs ->
    -x_positive + x_negative <= x_bfs  -> x_negative <= x_bfs

    also
    Ax <= b  ->  A(x_positive - x_negative + x_bfs) <= b  ->
    [A, -A] * [x_positive; x_negative] <= b

    """  

    num_constr, num_vars = A.shape

    y_bfs = np.dot(A, x_bfs).reshape([-1, 1])
    print("y_bfs:", y_bfs)
    b_prim = b - y_bfs
    print("b_prim:", b_prim)
    b_prim = np.vstack([b_prim, x_bfs.reshape([-1, 1])])
    print("b_prim:", b_prim)

    A_prim = np.hstack([A, -A])
    I = np.eye(num_vars)
    I_prim = np.hstack([-I, I])
    A_prim = np.vstack([A_prim, I_prim])

    c_prim = np.hstack([c, -c])
    d = np.dot(c, x_bfs)

    return A_prim, b_prim, c_prim, d


def lp(A, b, c):
    """
    maximize c * x 
    such that
    Ax <= b
    x >= 0
    """

    x_bfs = phase1(A, b, c)
    if x_bfs is None:
        return None, 2 # infeasible

    print("x_bfs:", x_bfs)

    print("b", b)
    A, b, c, d = phase1_5(A, b, c, x_bfs)
    print(A)
    print(b)
    print(c)
    print(d)

    x_opt, val = phase2(A, b, c)
    if x_opt is None:
        return None, 3 # unbounded

    return x_opt, 0 # optimal


def main():
    #A = np.array([[2, 1], [1, 2]])
    #b = np.array([[1], [1]])
    A = np.array([[2, 1], [1, 2], [1, 1]])
    b = np.array([[1], [1], [-1]])
    c = np.array([1, 1])

    print(lp(A, b, c))


if __name__ == '__main__':
    main()