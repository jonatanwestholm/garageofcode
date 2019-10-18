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

root = "0"
symbol_set = set([])

class WZ_Model:
    def __init__(self):
        self.S = {}
        self.G = defaultdict(dict)
        self.s = []
        self.rewind = 0
        self.top = 0
        self.symbol_set = symbol_set
        self.prime_with_symbol_set()

    def prime_with_symbol_set(self):
        for a in self.symbol_set:
            self.update(root, a, sym_splitter)

    def get_s(self):
        return self.s[len(self.symbol_set):]

    def get(self, seq, a):
        return self.G[seq][a]

    '''
    '''
    def update(self, seq, a, splitter):
        self.top += 1
        top = alph(self.top)
        self.S[top] = (seq, a)
        self.G[seq][a] = top
        
        for _ in range(self.rewind):
            self.s.pop() # remove last elements
        self.rewind = 0

        s = list(self.climb_to_root(seq))
        #print("match:", "".join(s))
        if splitter == ref_splitter:
            self.rewind = self.get_rewind("".join(s))
        #print("rewind:", self.rewind)
        #print()
        self.s.extend(s)
        self.s.append(a)

        return seq, a, splitter

    def update_double(self, seq0, seq1, splitter):
        a = next(self.climb_to_root(seq1))

        self.top += 1
        top = alph(self.top)
        self.S[top] = (seq0, a)
        self.G[seq0][a] = top
        
        '''
        for _ in range(self.rewind):
            self.s.pop() # remove last elements
        self.rewind = 0

        #print("match:", "".join(s))
        if splitter == ref_splitter:
            self.rewind = self.get_rewind("".join(s))
        #print("rewind:", self.rewind)
        #print()
        '''
        s = self.climb_to_root(top)
        self.s.extend(s)

        #return seq, a, splitter

    def climb_to_root(self, seq):
        stack = []
        while seq != root:
            seq, a = self.S[seq]
            stack.append(a)
        return reversed(stack)

    def get_rewind(self, s):
        if all([ch in alphabet for ch in s]):
            return 0

        m = s.rstrip(alphabet)
        return len(s) - len(m) + 1

    def can_be_stripped(self, seq):
        s = "".join(self.climb_to_root(seq))
        rewind = self.get_rewind(s)
        return rewind

def encode(reader):
    global symbol_set

    seq = root
    seq_old = root
    s = reader.read()
    symbol_set = set(s)
    model = WZ_Model()
    N = len(s)
    if not N:
        return
    idx = 0
    prev_seq = model.get(seq, s[0])
    prev_splitter = sym_splitter
    idx += 1

    while idx < N:
        a = s[idx]
        seq_old = seq

        try:
            seq = model.get(seq, a)
        except KeyError:
            '''
            rewind = model.can_be_stripped(seq)
            if rewind > 0:
                splitter = ref_splitter
                idx -= rewind
            else:
                splitter = sym_splitter
            '''
            yield prev_seq, prev_splitter
            splitter = sym_splitter
            model.update_double(prev_seq, seq, prev_splitter)
            prev_seq = seq
            prev_splitter = splitter
            seq = root

        idx += 1

    if seq != root:
        yield prev_seq, prev_splitter
        model.update_double(prev_seq, seq, prev_splitter)

    print("end of encoding")
    print("G encode:", model.G)
    print("S encode:", model.S)
    print(model.s)

def decode(reader):
    model = WZ_Model()
    reader = iter(reader.read())
    prev_seq, prev_splitter = get_id(reader)

    while True:
        try:
            seq, splitter = get_id(reader)
        except StopIteration:
            break

        model.update_double(prev_seq, seq, prev_splitter)
        prev_seq = seq
        prev_splitter = splitter

    yield from model.get_s()
    print("G decode:", model.G)
    print("S encode:", model.S)
    print(model.s)


def get_id(reader):
    id_num = []
    while True:
        a = next(reader)
        #print("digit", a)
        if a not in enc_alphabet:
            return "".join(id_num), a
        else:
            id_num.append(a)


def alph(seq):
    """
    Convert an int in base-10 to
    base-whatever length the alphabet is
    Assumes 0 is the 0
    """
    if not seq:
        return root
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
    #fn = "/home/jdw/garageofcode/data/compression/nilsholg.txt"
    #fn = "/home/jdw/garageofcode/data/compression/medium.txt"
    #fn = "short.txt"
    fn = "veryshort.txt"
    fn_compressed = fn.split(".")[0] + ".wzip"
    fn_reconstructed = fn.split(".")[0] + "_rec.txt"
    # encoding step
    with open(fn, "r") as r:
        with open(fn_compressed, "w") as f:
            for seq, spl in encode(r):
                #if a is None:
                #    f.write("{}{}".format(seq, ref_splitter))
                #else:
                f.write("{}{}".format(seq, spl))
    
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
