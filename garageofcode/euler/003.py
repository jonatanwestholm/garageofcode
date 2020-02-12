import time
from math import sqrt, ceil
from eulerutils import get_primes

t0 = time.time()
n = 600851475143
#n = 91
largest_p = 1
factors = []

while True:
    for p in get_primes(n):
        if n % p == 0:
            largest_p = p
            n = n / p
            factors.append(p)
            break
    else:
        t1 = time.time()
        print("Time: {0:.3f}".format(t1 - t0))
        print(factors)
        print("Largest prime:", largest_p)
        break