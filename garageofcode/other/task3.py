import time
from collections import Counter

import numpy as np
    
def solution(A):
    counter = Counter(A)
    return min(int(sum([n*(n-1) / 2 for n in counter.values()])), 1000000000)


def count_occurences(A):
    d = {}
    for elem in A:
        if elem in d:
            d[elem] += 1
        else:
            d[elem] = 1
    return d

def solution2(A):
    counter = count_occurences(A)
    return min(int(sum([n*(n-1) / 2 for n in counter.values()])), 1000000000)


for _ in range(100):
    test_set = np.random.randint(0, 100, size=0)
    t0 = time.time()
    s1 = solution(test_set)
    t1 = time.time()
    s2 = solution2(test_set)
    t2 = time.time()

    #print(t1 - t0)
    #print(t2 - t1)
    if s1 != s2:
        print("Error!")
        break

print(solution([]))