"""
By replacing the 1st digit of the 2-digit number *3, 
it turns out that six of the nine possible values: 
13, 23, 43, 53, 73, and 83, are all prime.

By replacing the 3rd and 4th digits of 56**3 with the same digit, 
this 5-digit number is the first example having seven get_primes 
among the ten generated numbers,
yielding the family: 56003, 56113, 56333, 56443, 56663, 56773, and 56993. 
Consequently 56003, being the first member of this family, 
is the smallest prime with this property.

Find the smallest prime which, by replacing part of the number 
(not necessarily adjacent digits) with the same digit, 
is part of an eight prime value family.
"""

import numpy as np
from itertools import combinations

from eulerutils import get_primes

def get_patterns(num_digits, num_pattern):
    locs = list(range(num_digits - 1))
    for pat in combinations(locs, num_digits - num_pattern - 1):
        pat = list(pat) + [num_digits - 1]
        print(pat)
        yield pat

def get_numbers(pat, num_digits, fill):
    num_free = len(pat)
    N = 10**num_free
    for i in range(N // 10 + 1, N, 2):
        digits = [int(ch) for ch in str(i)]
        a = np.ones(num_digits)*fill
        a[pat] = digits
        yield digits2num(a)

def is_prime(n, ps):
    cutoff = np.sqrt(n)
    for p in ps:
        if n % p == 0:
            return False
    else:
        return True

def pat2diff(pat, num_digits):
    digits = np.ones([num_digits])
    for i in pat:
        digits[i] = 0
    return digits2num(digits)

def digits2num(digits):
    """left-to-right reading of decimal number as array
    """
    return sum([d * 10**i for i, d in enumerate(digits[::-1])])

def main():
    min_family = 8
    
    num_digits = 6
    num_pattern = 3
    fill = 0
    N = 10**num_digits

    primes = list(get_primes(np.sqrt(N)))
    print("made all primes")

    for pat in get_patterns(num_digits, num_pattern):
        diff = pat2diff(pat, num_digits)
        for num in get_numbers(pat, num_digits, fill):
            num_prime = sum([is_prime(num + i * diff, primes) for i in range(10)])
            if num_prime >= min_family:
                print(num)
                for i in range(10):
                    print(num + i * diff)
                print([is_prime(num + i * diff, primes) for i in range(10)])
                return
    else:
        print("found none")


if __name__ == '__main__':
    main()

'''
def main():
    num_digits = 6
    N = 10**num_digits

    r = 2
    min_family = 8

    ps = [2]
    s = 0

    for p in get_primes(N, [2], 3):
        ps.append(p)
        if p < N / 10:
            continue
        if not s:
            print("made all get_primes")
            s = 1
        #print(p)
        pattern = [i for i, ch in enumerate(str(p)) if ch == "1"]
        if len(pattern) < r:
            continue
        for pat in get_patterns(pattern, num_digits, r):
            num_family = 1 + sum([is_prime(p + i * pat, ps) for i in range(1, 10)])
            if num_family >= min_family:
                print(p)
                return
'''
