"""
The following iterative sequence is defined for the set of positive integers:

n → n/2 (n is even)
n → 3n + 1 (n is odd)

Using the rule above and starting with 13, we generate the following sequence:

13 → 40 → 20 → 10 → 5 → 16 → 8 → 4 → 2 → 1
It can be seen that this sequence (starting at 13 and finishing at 1) contains 10 terms. 
Although it has not been proved yet (Collatz Problem), 
it is thought that all starting numbers finish at 1.

Which starting number, under one million, produces the longest chain?

NOTE: Once the chain starts the terms are allowed to go above one million.
"""

import time

memo = {1: 1}

def collatz(n):
    if n in memo:
        return memo[n]

    if n % 2 == 0:
        val = 1 + collatz(n / 2)
        memo[n] = val
        return val
    else:
        val = 1 + collatz(3*n + 1)
        memo[n] = val
        return val

t0 = time.time()
longest = 0
best_n = None
for n in range(1, int(1e6)):
    chain_length = collatz(n)
    if chain_length > longest:
        longest = chain_length
        best_n = n

t1 = time.time()
print("Time: {0:.3f}".format(t1- t0))
print(best_n, longest)