from collections import Counter

def elems(S):
    for si in S:
        yield from si

def smallest_unique_set(S, subset=None):
    if subset is None:
        subset = set(elems(S))
    for si in S:
        if not subset - set(si):
            raise ValueError("No unique set exists")
    p = []
    while S:
        c = Counter(elems(S))
        if len(c) < len(subset):  
            # it will break after this
            r = next(iter(subset - set(c)))
            p.append(r)
            break        
        else:
            r = c.most_common()[-1][0]
            p.append(r)
            S = [si for si in S if r in si]
    return p


def main():
    S = [[1, 2], [1, 2, 3], [1, 3], [2, 3], [3, 4]]
    print(smallest_unique_set(S))


if __name__ == '__main__':
    main()