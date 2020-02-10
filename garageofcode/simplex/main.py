import numpy as np

# or-tools convention
status2str = ["OPTIMAL", "FEASIBLE", "INFEASIBLE", "UNBOUNDED", 
              "ABNORMAL", "MODEL_INVALID", "NOT_SOLVED"]

debug = False
def dbg(s0, *s):
    if debug:
        print(s0, *s)

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

    #dbg(T)

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
    dbg("z_init:\n", z_init)
    x_relaxed = np.concatenate([np.zeros([num_vars, 1]), z_init])
    dbg("x_relaxed:\n", x_relaxed)
    A_prim, b_prim, c_prim, d_prim = phase1_5(A_ext, b, c_ext, x_relaxed)
    #c_prim[-len(c_prim) // 2:] = 0
    dbg("A_prim:\n", A_prim)
    dbg("b_prim:\n", b_prim)
    dbg("c_prim:\n", c_prim)
    dbg("d_prim:\n", d_prim)

    x_bfs, val = phase2(A_prim, b_prim, c_prim)

    dbg("x_bfs:", x_bfs, "val:", val, "d:", d_prim)
    #exit(0)

    # c_ext * [0 z] = c_prim * x_bfs + d_prim = val + d_prim

    tol = 1e-8
    if val + d_prim < -tol: # infeasible
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
    dbg("y_bfs:", y_bfs)
    b_prim = b - y_bfs
    dbg("b_prim:", b_prim)
    b_prim = np.vstack([b_prim, x_bfs.reshape([-1, 1])])
    dbg("b_prim:", b_prim)

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

    num_constr, num_vars = A.shape

    x_bfs = phase1(A, b, c)
    if x_bfs is None:
        return None, None, 2 # infeasible

    dbg("x_bfs:", x_bfs)

    dbg("b", b)
    A, b, c, d = phase1_5(A, b, c, x_bfs)
    dbg(A)
    dbg(b)
    dbg(c)
    dbg(d)

    x_opt, val = phase2(A, b, c)
    if x_opt is None:
        return None, np.inf, 3 # unbounded

    x_opt = x_opt[:num_vars] - x_opt[-num_vars:]
    x_opt = x_opt + x_bfs
    return x_opt, val, 0 # optimal


def main():
    global debug
    debug = False

    all_tests = ["basic", "basic_2", "basic_3",
                 "basic_4", "basic_5",
                  "infeasible", "infeasible_2",
                  "unbounded"]

    test_cases = ["basic_5"]

    if "basic" in test_cases:
        A = np.array([[2, 1], [1, 2]])
        b = np.array([[1], [1]])
        c = np.array([1, 1])
        print("Should be OPTIMAL")
        x_opt, opt_val, status = lp(A, b, c)
        print(x_opt, opt_val, status2str[status])

    if "basic_2" in test_cases:
        A = np.array([[2, 1], [1, 2], [4, 4]])
        b = np.array([[1], [1], [1]])
        c = np.array([1, 1])
        print("Should be OPTIMAL")
        x_opt, opt_val, status = lp(A, b, c)
        print(x_opt, opt_val, status2str[status])

    if "basic_3" in test_cases:
        A = np.array([[2, 1], [1, 2], [-2, -2]])
        b = np.array([[1], [1], [-1]])
        c = np.array([1, 1])
        print("Should be OPTIMAL")
        x_opt, opt_val, status = lp(A, b, c)
        print(x_opt, opt_val, status2str[status])

    if "basic_4" in test_cases:
        A = np.array([[3, 1], [1, 3], [2, 3]])
        b = np.array([[1], [1], [1]])
        c = np.array([1, 1])
        print("Should be OPTIMAL")
        x_opt, opt_val, status = lp(A, b, c)
        print(x_opt, opt_val, status2str[status])

    if "basic_5" in test_cases:
        # this should take just two pivots
        A = np.array([[-1, 1], [1, -1], [1, 1]])
        b = np.array([[1], [1], [10000000]])
        c = np.array([1, 1])
        print("Should be OPTIMAL")
        x_opt, opt_val, status = lp(A, b, c)
        print(x_opt, opt_val, status2str[status])

    if "infeasible" in test_cases:
        A = np.array([[2, 1], [1, 2], [1, 1]])
        b = np.array([[1], [1], [-1]])
        c = np.array([1, 1])
        print("Should be INFEASIBLE")
        x_opt, opt_val, status = lp(A, b, c)
        print(x_opt, opt_val, status2str[status])

    if "infeasible_2" in test_cases:
        A = np.array([[2, 1], [1, 2], [-1, -1]])
        b = np.array([[1], [1], [-1]])
        c = np.array([1, 1])
        print("Should be INFEASIBLE")
        x_opt, opt_val, status = lp(A, b, c)
        print(x_opt, opt_val, status2str[status])

    if "unbounded" in test_cases:
        A = np.array([[-1, -1]])
        b = np.array([[-1]])
        c = np.array([1, 1])
        print("Should be UNBOUNDED")
        x_opt, opt_val, status = lp(A, b, c)
        print(x_opt, opt_val, status2str[status])


if __name__ == '__main__':
    main()