from itertools import permutations

import numpy as np
import matplotlib.pyplot as plt

n = None
m = None

def d(a, b, N):
    """Wrapped distance"""

    if b < a:
        tmp = a
        a = b
        b = tmp

    return min(b - a, N - (b - a))

def d2(x, y):
    return d(x[0], y[0], m)**2 + d(x[1], y[1], n)**2

def enumerate2d(A):
    for j0, row in enumerate(A):
        for i0, (i1, j1) in enumerate(row):
            yield (i0, j0), (i1, j1)

def score(A):
    s = 0
    for x0, x1 in enumerate2d(A):
        #print(x0)
        for y0, y1 in enumerate2d(A):
            #print("\t", y0)
            #print(x0, y0)
            #print(x1, y1)
            #print(d2(x0, y0) * d2(x1, y1))
            #print()
            s += d2(x0, y0) * d2(x1, y1)
    return s / 2

def score_map(A):
    S = np.zeros([len(A), len(A[0])])
    for x0, x1 in enumerate2d(A):
        s = 0
        for y0, y1 in enumerate2d(A):
            s += d2(x0, y0) * d2(x1, y1)
        S[x0[0], x0[1]] = s / 2
    return S

def lb_score(A):
    dists = []

    for x0, _ in enumerate2d(A):
        for y0, _ in enumerate2d(A):
            dists.append(d2(x0, y0))
        break

    dists = dists[1:]
    dists = np.array(sorted(dists))
    return np.dot(dists, dists[::-1]) * n * m / 2

def get_board(n, m):
    return [[(i, j) for i in range(m)] for j in range(n)]

def get_1d_opt(n):
    if n % 2 == 1:
        return [2*i % n for i in range(n)]
    else:
        # not really optimal
        first = list(range(0, n, 2))
        second = list(range(1, n, 2))
        return first + second

def solve_1d_perm(A):
    n = len(A)
    m = len(A[0])

    perm_rows = get_1d_opt(n)
    perm_cols = get_1d_opt(m)
    A = [A[i] for i in perm_rows]
    A = list(zip(*A))
    A = [A[i] for i in perm_cols]
    A = list(zip(*A))
    return A

def opt_perm(A):
    best_score = score(A)
    best_B = A

    for B in permutations(A):
        s = score(B)
        if s < best_score:
            best_score = s
            best_B = B

    print("best score:", best_score)
    print(best_B)

def main():
    global n
    global m

    n = 19
    m = 19

    A = get_board(n, m)

    #print(A)
    #print(A)
    print("naive score:", score(A))
    print("lb score   :", lb_score(A))

    B = solve_1d_perm(A)
    print("1dopt score:", score(B))
    #[print(row) for row in B]
    S = score_map(B)
    print(S)
    plt.imshow(S)
    plt.show()


if __name__ == '__main__':
    main()