"""
The arithmetic sequence, 1487, 4817, 8147, in which each of the terms increases by 3330, 
is unusual in two ways: (i) each of the three terms are prime, and, 
(ii) each of the 4-digit numbers are permutations of one another.

There are no arithmetic sequences made up of three 1-, 2-, or 3-digit primes, 
exhibiting this property, but there is one other 4-digit increasing sequence.

What 12-digit number do you form by concatenating the three terms in this sequence?
"""

from itertools import groupby, combinations

from eulerutils import primes

def sorted_digits(n):
    return int("".join(sorted(str(n))))

def find_triplet(numbers):
    for a0, a1, a2 in combinations(numbers, 3):
        if a0 - a1 == a1 - a2:
            return (a0, a1, a2)

    return None

ps = list(primes(10000))
ps = [p for p in ps if p >= 1000]
ps = [(sorted_digits(p), p) for p in ps]

for key, anagrams in groupby(sorted(ps), key=lambda x: x[0]):
    anagrams = [elem[1] for elem in anagrams]
    #print(key, anagrams)
    #if len(anagrams) >= 3:
    #   print(anagrams)
    triplet = find_triplet(anagrams)
    if triplet:
        print(triplet)