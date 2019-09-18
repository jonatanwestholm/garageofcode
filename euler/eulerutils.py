from math import sqrt, ceil

def primes(n, memo=None, i0=2):
    if memo is None:
        memo = []
    i = i0
    while i <= n:
        for p in memo:
            if i % p == 0:
                break
        else:
            yield i
            memo.append(i)
        i += 1
    return memo

def factorize(n, memo=None):
    if memo is None:
        memo = []
    factors = []
    p = 1
    n0 = n
    while True:
        for p in primes(n, memo, p+1):
            while n % p == 0:
                factors.append(p)
                n = n / p
            if p in factors:
                break
        else:
            break
    return factors

if __name__ == '__main__':
    print(factorize(24))