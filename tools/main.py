def permutations(iterable, r=None):
    """
    Investigating itertool's permutation to see how it works
    """
    # permutations('ABCD', 2) --> AB AC AD BA BC BD CA CB CD DA DB DC
    # permutations(range(3)) --> 012 021 102 120 201 210
    pool = tuple(iterable)
    n = len(pool)
    r = n if r is None else r
    if r > n:
        return
    indices = list(range(n))
    cycles = list(range(n, n-r, -1))
    yield tuple(pool[i] for i in indices[:r])
    while n:
        for i in reversed(range(r)):
            print("i:", i)
            print("indices:", indices)
            print("cycles:", cycles)
            print()
            cycles[i] -= 1
            if cycles[i] == 0:
                indices[i:] = indices[i+1:] + indices[i:i+1]
                cycles[i] = n - i
            else:
                j = cycles[i]
                indices[i], indices[-j] = indices[-j], indices[i]
                print("cycles before yield:", cycles)
                yield tuple(pool[i] for i in indices[:r])
                break
        else:
            return

def powerset(iterable):
    """
    Yields all subsets of iterable
    Considers same element at different positions as different

    Example:
    powerset('ABC') --> '', 'A', 'B', 'AB', 'C', 'AC', 'BC', 'ABC'
    """
    n = len(iterable)
    includes = [False] * n
    while True:
        yield [item for item, include in zip(iterable, includes) 
               if include]        
        prop = True
        for idx, inc in enumerate(includes):
            inc, prop = inc ^ prop, inc & prop
            includes[idx] = inc
            if inc:
                break
        else:
            return

def powerset_(iterable):
    """
    Smart-alec's powerset
    """
    n = len(iterable)
    for k in range(2**n):
        includes = [ch == "1" for ch in reversed(bin(k)[2:])]
        yield [item for item, include in zip(iterable, includes) if include]

def powerset__(iterable):
    """
    Plagiator's powerset
    """
    from itertools import combinations
    n = len(iterable)
    for k in range(n+1):
        yield from combinations(iterable, k)

def powerset___(iterable):
    """
    Recursion-addict's powerset
    """
    if not iterable:
        yield []
    else:
        s = iterable[0]
        for subset in powerset___(iterable[1:]):
            yield subset
            yield [s] + subset

if __name__ == '__main__':
    iterable = "ABCD"
    for seq in powerset___(iterable):
        print("Sequence:", seq)