import os
from collections import Counter, defaultdict, deque

import numpy as np
import matplotlib.pyplot as plt

splitter = " "
ref_splitter = "_"
alphabet = "abcdefghijklmnopqrstuvwxyzåäö"
alphabet = alphabet + alphabet.upper()

#enc_alphabet = "abcdefghijklmnopqrstuvwxyz"
#enc_alphabet = enc_alphabet + enc_alphabet.upper()
#enc_alphabet = "0123456789,;.:-_!%&/()?" + enc_alphabet
enc_alphabet = "0123456789"
b = len(enc_alphabet)

def encode(reader):
    def get_next(reader):
        nonlocal backstep
        nonlocal queue
        nonlocal nextqueue
        while True:
            if backstep:
                try:
                    yield queue.popleft()
                except IndexError:
                    backstep = False
                    queue = nextqueue
                    nextqueue = deque()
            else:
                try:
                    yield next(reader)
                except StopIteration:
                    break

    G = defaultdict(dict)  # phrase tree
    seq = 0  # sequence id.
    top = 0  # highest id in use
    queue = deque()  # symbols since last non-alphabetic
    nextqueue = deque()
    backstep = False
    match = []
    seq_old = seq
    for idx, a in enumerate(get_next(iter(reader.read()))):
        seq_old = seq
        if backstep:
            nextqueue.append(a)
        else:
            if a in alphabet:
                queue.append(a)
            else:
                queue.clear()

        try:
            seq = G[seq][a]
            if not backstep:
                match.append(a)
        except KeyError:
            if matches(G, queue) and not backstep:
                m = strip(match)
                if not len(m) + len(queue) - 1 == len(match):
                    print("queue", queue)
                    print("m", m)
                    print("match", match)
                    print()
                emit = matches(G, m)
                yield emit, None
            else:
                #print(match)
                emit, b = traverse(G, match)
                if b is None:
                    yield emit, a
                else:
                    yield emit, b
                '''
                '''
                #yield seq, a
            top += 1
            G[seq][a] = top #alph(top)  # extend tree
            backstep = True  # go back in search to latest non-alphabetic
            if 0: #idx >= 5000000 and idx < 5000500:
                print("match:", "".join(match))
                print("queue:", "".join(queue))
                print("seq, a:", seq, a)
                print()
                #if idx > 100:
                #    break
            seq = 0  # restart at root
            match = []
    if seq_old:
        yield seq_old, a

    if 0:
        num_entries = sum(map(len, G.values()))
        #print(num_entries)
        #d, freqs = zip(*sorted(depths.items()))
        msg_length = sum([d_num * freq for d_num, freq in depths.items()])
        avg_depth = msg_length / num_entries
        print("avg_depth: {0:.2f}".format(avg_depth))
        print(G)


def matches(G, queue):
    """
    If the sequence in 'queue' correspond to a
    node in 'G', return the sequence id, 
    otherwise return False
    """
    if not queue:
        return False
    seq = 0
    for a in queue:
        try:
            seq = G[seq][a]
        except KeyError:
            return False
    return seq


def traverse(G, s):
    """
    Get the sequence id that corresponds to
    the longest match for s in G
    """
    seq = 0
    for a in s:
        try:
            seq = G[seq][a]
        except KeyError:
            return seq, a
    return seq, None


def test_matches():
    G = defaultdict(dict)
    G[0]["a"] = 1
    G[0]["b"] = 2
    G[1]["a"] = 3

    print("matches(G, ['a', 'a']):", matches(G, ["a", "a"]))
    print("matches(G, ['b']):", matches(G, ["b"]))
    print("matches(G, ['a']):", matches(G, ["a"]))
    print("matches(G, []):", matches(G, []))
    print("matches(G, ['a', 'a', 'a']):", matches(G, ["a", "a", "a"]))
    print("matches(G, ['a', 'b']):", matches(G, ["a", "b"]))
    print("matches(G, ['c']):", matches(G, ["c"]))


def alph(seq):
    """
    Convert an int in base-10 to
    base-whatever length the alphabet is
    Don't send in 0
    """
    s = []
    quot = seq
    while quot:
        quot, rest = quot // b, quot % b
        s.append(enc_alphabet[rest])
    return "".join(reversed(s))


def strip(match):
    """
    If string contains nonalphabetic symbols, 
    strip the final run of alphabetic symbols.
    >>> "abcde fg" -> "abcde "

    If no nonalphabetics, return all
    >>> "abc" -> "abc"
    """
    has_nonalph = any([ch not in alphabet for ch in match])
    if not has_nonalph:
        return match
    else:
        m = match[:]
        while True:
            ch = m[-1]
            if ch not in alphabet:
                break
            else:
                m.pop()
        return m

def test_strip():
    strings = ["", "abcde fg", "abcde", "abcde.''\n fg.''\n rt"]
    for s in strings:
        print("strip({})".format(s), strip([ch for ch in s]))

def decode(reader):
    G = defaultdict(dict)
    S = {}  # child -> (parent, symbol) mapping in phrase tree
    top = 0
    old_match = []
    reader = iter(reader.read())
    while True:
        try:
            seq, spl = get_id(reader)
        except StopIteration:
            break
        if old_match:
            new_match = list(climb_to_root(S, seq))
            fill_seq, a = traverse(G, old_match + new_match)
            top += 1
            S[top] = (fill_seq, a)
            G[fill_seq][a] = top
            old_match = []

        if spl == splitter:
            a = next(reader)
            #print("a", a)
            yield from climb_to_root(S, seq)
            yield a
            top += 1
            S[top] = (seq, a)
            G[seq][a] = top
        elif spl == ref_splitter:
            old_match = list(climb_to_root(S, seq))
            yield from old_match

    print("G:", G)

def get_id(reader):
    id_num = []
    while True:
        a = next(reader)
        #print("digit", a)
        if a not in "0123456789":
            return int("".join(id_num)), a
        else:
            id_num.append(a)

def climb_to_root(S, seq):
    """
    The annoying thing about this function is 
    that it must go all the way to the root
    before starting to yield anything.
    Can that be avoided?
    """
    stack = []
    while seq:
        seq, a = S[seq]
        stack.append(a)
    #print("".join(reversed(stack)))
    for a in reversed(stack):
        yield a

def main():
    #fn = "/home/jdw/garageofcode/data/compression/nilsholg2.txt"
    #fn = "/home/jdw/garageofcode/data/compression/nilsholg.txt"
    #fn = "short.txt"
    fn = "veryshort.txt"
    fn_compressed = fn.split(".")[0] + ".wzip"
    fn_reconstructed = fn.split(".")[0] + "_rec.txt"
    # encoding step
    with open(fn, "r") as r:
        with open(fn_compressed, "w") as f:
            for seq, a in encode(r):
                if a is None:
                    f.write("{}{}".format(seq, ref_splitter))
                else:
                    f.write("{}{}{}".format(seq, splitter, a))
    
    print("Before ", os.stat(fn).st_size)
    print("After  ", os.stat(fn_compressed).st_size)

    #exit(0)

    with open(fn_compressed, "r") as r:
        with open(fn_reconstructed, "w") as f:
            for a in decode(r):
                #if a == "\\n":
                #    f.write("\n")
                #else:
                f.write(a)

    res = os.system("diff {} {}".format(fn, fn_reconstructed))
    if res:
        print("Reconstruction: failed")
    else:
        print("Reconstruction: OK")

if __name__ == '__main__':
    main()

    #test_matches()
    #test_strip()