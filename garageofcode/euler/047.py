"""
The first two consecutive numbers to have two distinct prime factors are:

14 = 2 × 7
15 = 3 × 5

The first three consecutive numbers to have three distinct prime factors are:

644 = 2² × 7 × 23
645 = 3 × 5 × 43
646 = 2 × 17 × 19.

Find the first four consecutive integers to have four distinct prime factors each. 
What is the first of these numbers?
"""

from eulerutils import factorize

min_distinct = 4
min_consec = 4

memo = {1: 0}
primes = []

def find_smallest_factor(n):
    for p in primes:
        if n % p == 0:
            return p
    else:
        return None

def distinct_enough(n):
    n0 = n
    p = find_smallest_factor(n)
    if p is None:
        primes.append(n)
        memo[n] = 1
    else:
        while n % p == 0:
            n = n / p
        memo[n0] = 1 + memo[n]

    return memo[n0] >= min_distinct

consec = 0
i = 1
while True:
    i += 1
    #if i % 100 == 0:
    #    print(i)
    if distinct_enough(i):
        consec += 1
        if consec >= min_consec:
            print(i - min_consec + 1)
            break
    else:
        consec = 0