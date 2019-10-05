from itertools import chain, combinations

def powerset(s):
    return chain.from_iterable(combinations(s, r) for in range(len(s) + 1))


def ncube_corners(n):
    dims = list(range(n))
    A = np.zeros([2**n, n])
    for i, corner in enumerate(powerset(dims)):
        for j in corner:
            a[i, j] = 1
    return A


def main():
    n = 2
    points = ncube_corners(n)

    

if __name__ == '__main__':
    main()