from math import sqrt, ceil
from eulerutils import primes

n = 600851475143
#n = 91
largest_p = 1
factors = []

while True:
    for p in primes(n):
        if n % p == 0:
            largest_p = p
            n = n / p
            factors.append(p)
            break
    else:
        print(factors)
        print("Largest prime:", largest_p)
        break