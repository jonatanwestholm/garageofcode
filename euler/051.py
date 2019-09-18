"""
By replacing the 1st digit of the 2-digit number *3, 
it turns out that six of the nine possible values: 13, 23, 43, 53, 73, and 83, are all prime.

By replacing the 3rd and 4th digits of 56**3 with the same digit, 
this 5-digit number is the first example having seven primes among the ten generated numbers,
yielding the family: 56003, 56113, 56333, 56443, 56663, 56773, and 56993. 
Consequently 56003, being the first member of this family, 
is the smallest prime with this property.

Find the smallest prime which, by replacing part of the number 
(not necessarily adjacent digits) with the same digit, 
is part of an eight prime value family.
"""

import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import numpy as np
from itertools import combinations

from eulerutils import primes

'''
def get_patterns(num_digits):
    for i in range(1, 2**num_digits):
        pat = int("{1:0{0:d}d}".format(num_digits, int(bin(i)[2:])))
        #print(pat)
        yield pat

def get_patterns(pattern, num_digits, r):
    for pat in combinations(pattern, r):
        a = np.zeros([num_digits])
        for i in pat:
            a[i] = 1
        s = sum([c * 10**i for i, c in enumerate(a[::-1])])
        if s % 2 == 0 and s % 3 == 0 and s % 5 == 0:
            yield s
'''

def get_patterns(num_digits, r):
    locs = list(range(num_digits))
    for pat in combinations(locs, r):
        yield pat
        '''
        a = np.zeros([num_digits])
        for i in pat:
            a[i] = 1
        s = sum([c * 10**i for i, c in enumerate(a[::-1])])
        if s % 2 == 0 and s % 3 == 0 and s % 5 == 0:
            yield a
        '''

def get_numbers(pat, num_digits, fill):
    num_free = num_digits - len(pat)
    for i in range(1, num_free, 2):
        pass


def is_prime(n, ps):
    cutoff = np.sqrt(n)
    for p in ps:
        if p > cutoff:
            return True
        if n % p == 0:
            return False
    else:
        print("warning! ran out of primes")
        return False

def main():
    num_digits = 6
    N = 10**num_digits

    r = 2
    min_family = 8

    ps = [2]
    s = 0

    for p in primes(N, [2], 3):
        ps.append(p)
        if p < N / 10:
            continue
        if not s:
            print("made all primes")
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


if __name__ == '__main__':
    #main()

    print(list(get_patterns(6, 2)))