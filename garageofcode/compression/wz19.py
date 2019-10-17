import os
from collections import Counter, defaultdict, deque

import numpy as np
import matplotlib.pyplot as plt

sym_splitter = " "
ref_splitter = "_"
alphabet = "abcdefghijklmnopqrstuvwxyzåäö"
alphabet = alphabet + alphabet.upper()

enc_alphabet = "abcdefghijklmnopqrstuvwxyz"
enc_alphabet = enc_alphabet + enc_alphabet.upper()
enc_alphabet = "0123456789" + enc_alphabet
#enc_alphabet = "0123456789"
b = len(enc_alphabet)

class WZ_Model:
    def __init__(self):
        self.S = {}
        self.G = defaultdict(dict)
        self.s = []
        self.rewind = 0
        self.top = 0

    def get(self, seq, a):
        return self.G[seq][a]

    def update(self, seq, a, splitter):
        self.top += 1
        top = alph(self.top)
        self.S[top] = (seq, a)
        self.G[seq][a] = top
        
        for _ in range(self.rewind):
            self.s.pop() # remove last elements
        self.rewind = 0

        s = list(self.climb_to_root(seq))
        if splitter == ref_splitter:
            self.rewind = self.get_rewind("".join(s))
        self.s.extend(s)
        self.s.append(a)

        return seq, a, splitter

    def climb_to_root(self, seq):
        stack = []
        while seq != "0":
            seq, a = self.S[seq]
            stack.append(a)
        return reversed(stack)

    def get_rewind(self, s):
        if all([ch in alphabet for ch in s]):
            return 0

        m = s.rstrip(alphabet)
        return len(s) - len(m) - 1

    def can_be_stripped(self, seq):
        s = "".join(self.climb_to_root(seq))
        #if seq == "5":
        #    print("5 seq:", [ch for ch in s])
        rewind = self.get_rewind(s)
        #if seq == "5":
        #    print("rewind:", rewind)
        return rewind

def encode(reader):
    model = WZ_Model()
    seq = "0"
    seq_old = "0"
    s = reader.read()
    N = len(s)
    idx = 0

    while idx < N:
        a = s[idx]
        seq_old = seq

        try:
            seq = model.get(seq, a)
        except KeyError:
            rewind = model.can_be_stripped(seq)
            if rewind > 0:
                splitter = ref_splitter
                idx -= rewind
            else:
                splitter = sym_splitter
            yield model.update(seq, a, splitter)
            seq = "0"

        idx += 1

    if seq != "0":
        yield model.update(seq_old, a, sym_splitter)

    #print("end of encoding")
    #print("G encode:", model.G)
    #print("S encode:", model.S)
    #print(model.s)

def decode(reader):
    model = WZ_Model()
    reader = iter(reader.read())

    while True:
        try:
            seq, splitter = get_id(reader)
        except StopIteration:
            break

        #yield from model.climb_to_root(seq)

        a = next(reader)
        #yield a

        model.update(seq, a, splitter)

    yield from model.s
    #print("G decode:", model.G)
    #print("S encode:", model.S)
    #print(model.s)


def get_id(reader):
    id_num = []
    while True:
        a = next(reader)
        #print("digit", a)
        if a not in enc_alphabet:
            return "".join(id_num), a
        else:
            id_num.append(a)

'''
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
'''

def alph(seq):
    """
    Convert an int in base-10 to
    base-whatever length the alphabet is
    Assumes 0 is the 0
    """
    if not seq:
        return "0"
    s = []
    quot = seq
    while quot:
        quot, rest = quot // b, quot % b
        s.append(enc_alphabet[rest])
    return "".join(reversed(s))


def test_alph():
    for seq in range(11):
        print("alph({}): {}".format(seq, alph(seq)))


default_dbg = False
def debug(*s, dbg=False):
    if default_dbg or dbg:
        print(*s)


def main():
    #fn = "/home/jdw/garageofcode/data/compression/nilsholg2.txt"
    fn = "/home/jdw/garageofcode/data/compression/nilsholg.txt"
    #fn = "/home/jdw/garageofcode/data/compression/medium.txt"
    #fn = "short.txt"
    #fn = "veryshort.txt"
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

    #test_alph()
