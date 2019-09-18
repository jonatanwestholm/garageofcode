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

from eulerutils import primes

def get_patterns(num_digits):
    for i in range(1, 2**num_digits):
        pat = int("{1:0{0:d}d}".format(num_digits, int(bin(i)[2:])))
        #print(pat)
        yield pat


def main():
    num_digits = 5
    N = 10**num_digits
    ps = primes(N)
    ps = [p for p in ps if p >= N / 10]

    min_family = 7

    for p in ps:
        for pat in get_patterns(num_digits):
            fam_size = 1 + sum([p + i * pat in ps for i in range(1, 9)])
            if fam_size >= min_family:
                print(p)
                break

if __name__ == '__main__':
    main()