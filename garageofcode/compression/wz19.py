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
    G = defaultdict(dict)  # phrase tree
    S = {}
    seq = 0  # sequence id.
    top = 0  # highest id in use
    match = []
    seq_old = seq
    s = list(iter(reader.read()))
    N = len(s)
    idx = 0
    debug([ch for ch in s], dbg=False)
    while idx < N:
        a = s[idx]
        seq_old = seq

        try:
            seq = G[seq][a]
            match.append(a)
        except KeyError:
            emit, b, rewind = backstep(G, match)
            #print(emit)
            if emit:
                #print("match:", "".join(match))
                #print()
                #print("emit:", )
                yield emit, b, ref_splitter
                idx -= rewind
            else:
                yield seq, a, splitter
            top += 1
            G[seq][a] = top  #alph(top)  # extend tree
            S[top] = (seq, a)
            seq = 0  # restart at root
            seq_old = 0
            match = []

        idx += 1

    if seq:
        yield seq_old, a, splitter

    debug("G encode:", G)
    debug("S encode:", S)


def backstep(G, match):
    if all([ch in alphabet for ch in match]):
        return False, None, None

    match = "".join(match)
    m = match.rstrip(alphabet)
    q = match[len(m):]
    if not matches(G, q):
        return False, None, None
    rewind = len(match) - len(m) + 1 # plus one, I think
    emit, r = traverse(G, m[:-1])
    assert r is None
    a = m[-1]
    #print("emit:", m[:-1], "+", [ch for ch in m[-1:]])
    return emit, a, rewind


def matches(G, s):
    """
    Check if these is a node in G
    that corresponds to sequence s
    """
    seq = 0
    for a in s:
        try:
            seq = G[seq][a]
        except KeyError:
            return False
    return True


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


default_dbg = False
def debug(*s, dbg=False):
    if default_dbg or dbg:
        print(*s)


def decode(reader):
    G = defaultdict(dict)
    S = {}  # child -> (parent, symbol) mapping in phrase tree
    top = 0
    reader = iter(reader.read())
    old_match = ""
    while True:
        try:
            seq, spl = get_id(reader)
        except StopIteration:
            break
        
        match = "".join(climb_to_root(S, seq))
        yield from match

        if old_match:
            debug("old_match", [ch for ch in old_match])
            debug("match", [ch for ch in match])
            full_match = old_match + match
            fill_seq, b = traverse(G, full_match)
            '''
            if b is None:
                print("seq:", seq)
                print("old_match", old_match)
                print("match", match)
                print("G:", G)
                print("S:", S)
            '''
            #assert b is not None
            if b is not None:
                debug("extending:")
                top += 1
                debug("fill_seq:", fill_seq, ", b:", b, ", top:", top)
                S[top] = (fill_seq, b)
                G[fill_seq][b] = top
                old_match = ""

        a = next(reader)
        yield a

        if spl == splitter:
            top += 1
            S[top] = (seq, a)
            G[seq][a] = top
        elif spl == ref_splitter:
            old_match = match + a

    debug("G:", G)
    debug("S:", S)


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
    #fn = "/home/jdw/garageofcode/data/compression/medium.txt"
    #fn = "short.txt"
    fn = "veryshort.txt"
    fn_compressed = fn.split(".")[0] + ".wzip"
    fn_reconstructed = fn.split(".")[0] + "_rec.txt"
    # encoding step
    with open(fn, "r") as r:
        with open(fn_compressed, "w") as f:
            for seq, a, spl in encode(r):
                #if a is None:
                #    f.write("{}{}".format(seq, ref_splitter))
                #else:
                f.write("{}{}{}".format(seq, spl, a))
    
    print("Before ", os.stat(fn).st_size)
    print("After  ", os.stat(fn_compressed).st_size)

    #  exit()

    with open(fn_compressed, "r") as r:
        with open(fn_reconstructed, "w") as f:
            for a in decode(r):
                #if a == "\\n":
                #    f.write("\n")
                #else:
                f.write(a)

    #exit()
    res = os.system("diff {} {}".format(fn, fn_reconstructed))
    if res:
        print("Reconstruction: failed")
    else:
        print("Reconstruction: OK")

if __name__ == '__main__':
    main()

    #test_matches()
    #test_strip()