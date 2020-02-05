import numpy as np

def lp(A, b, c):
    """
    maximize c * x 
    such that
    Ax <= b
    x >= 0
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

    num_slack = len(A)
    z_s0 = np.zeros([num_slack])
    z_s1 = np.zeros([num_slack, 1])

    T1 = np.hstack([np.array([1]), z_s0, c, np.array([0])])
    T2 = np.hstack([z_s1, np.eye(num_slack), A, b])
    T = np.vstack([T1, T2])

    print(T)

    basic = list(range(1, num_slack+1))

    while True:
        pc = select_pivot_column(T[0, 1:])
        if pc is None: # found optimum
            break
        print("pc:", pc)

        pr = select_pivot_row(T[1:, pc], T[1:, -1])
        if pr is None: # unbounded
            return None, np.inf
        print("pr:", pr)

        T = pivot(T, pc, pr)
        print(T)

        print("active var:", get_active_var(T[1:, pc]))
        basic[get_active_var(T[1:, pc])] = pc
        print("basic:", basic)

    return collect_solution(T, basic), -T[0, -1]


def collect_solution(T, basic):
    num_slack = len(basic)
    num_vars = len(T[0]) - num_slack - 2
    b = T[:, -1]

    solution = np.zeros([num_vars])

    for j in range(len(T[0, :-1])):
        if j not in basic or j <= num_slack:
            T[:, j] = 0

    for i, var_row in enumerate(T[1:]):
        if not sum(var_row[num_slack+1:-1]):
            continue

        ev = get_active_var(var_row[num_slack+1:-1])
        print("ev:", ev)
        print("var_row:", var_row)

        solution[ev] = T[i + 1, -1] / T[i + 1, ev + num_slack + 1]

    return solution


def get_active_var(a):
    return np.argmax(a)


def pivot(T, pc, pr):
    print("pc:", pc, "pr:", pr)
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

    print(Tc)
    if all(Tc <= 0): # can't select pivot row
        return None

    ratios = [bi / Tci if Tci > 0 else np.inf for Tci, bi in zip(Tc, b)]
    #print("ratios:", ratios)
    return np.argmin(ratios) + 1


def main():
    A = np.array([[2, 1], [1, 2], [4, 4]])
    b = np.array([[1], [1], [1]])
    c = np.array([1, 1])

    print(lp(A, b, c))


if __name__ == '__main__':
    main()