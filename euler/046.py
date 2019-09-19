"""
It was proposed by Christian Goldbach that 
every odd composite number can be written as the sum of a prime and twice a square.

9 = 7 + 2×12
15 = 7 + 2×22
21 = 3 + 2×32
25 = 7 + 2×32
27 = 19 + 2×22
33 = 31 + 2×12

It turns out that the conjecture was false.

What is the smallest odd composite that cannot be written as 
the sum of a prime and twice a square?
"""

import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from common.utils import Heap

primes = [2]

def is_prime(n):
    for p in primes:
        if n % p == 0:
            return False
    else:
        return True

def main():
    pairs = Heap(key=lambda x: x[0] + 2*x[1]**2)
    pairs.push((3, 0))

    old_key = 3
    while True:
        key, (p, k) = pairs.pop()
        print("{0:d} + 2*{1:d}^2 = {2:d}".format(p, k, key))

        if key - old_key > 2 and not is_prime(key):
            if not is_prime(key - 2):
                print("Num:", key - 2)
                print(primes)
                break

        if key != primes[-1] and is_prime(key):
            primes.append(key)
            pairs.push((key, 1))

        if key + 2 != primes[-1] and is_prime(key + 2):
            primes.append(key + 2)
            pairs.push((key + 2, 1))


        pairs.push((p, k + 1))
        old_key = key

if __name__ == '__main__':
    main()