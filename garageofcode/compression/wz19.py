import os
from collections import Counter, defaultdict, deque

import numpy as np
import matplotlib.pyplot as plt

splitter = " "
ref_splitter = "_"
alphabet = "abcdefghijklmnopqrstuvwxyzåäö"
alphabet = alphabet + alphabet.upper()

enc_alphabet = "abcdefghijklmnopqrstuvwxyz"
enc_alphabet = enc_alphabet + enc_alphabet.upper()
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

    def matches(G, queue):
        if not queue:
            return False
        seq = 0
        for a in queue:
            try:
                seq = G[seq][a]
            except KeyError:
                return False
        return True

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
        #s.append(alphabet[rest])
        return "".join(reversed(s))

    G = defaultdict(dict)  # phrase tree
    seq = "0"  # sequence id. I know it's a string, just trust me.
    top = 0  # highest id in use
    queue = deque()
    nextqueue = deque()
    backstep = False
    match = []
    depth = 0  # for statistics
    depths = Counter()  # for statistics
    for idx, a in enumerate(get_next(iter(reader.read()))):
        if backstep:
            nextqueue.append(a)
        else:
            if a in alphabet:
                queue.append(a)
            else:
                queue.clear()

        try:
            seq = G[seq][a]
            match.append(a)
            #if not backstep:
            depth += 1
        except KeyError:
            if matches(G, queue):
                yield seq, None
            else:
                yield seq, a
            top += 1
            G[seq][a] = alph(top)  # extend tree
            backstep = True  # go back in search to latest non-alphabetic
            if 0:
                print("match:", "".join(match))
                print("queue:", "".join(queue))
                print("seq, a:", seq, a)
                print()
                #if idx > 100:
                #    break
            seq = 0  # restart at root
            match = []
            depths[depth] += 1
            depth = 0

    num_entries = sum(map(len, G.values()))
    #print(num_entries)
    #d, freqs = zip(*sorted(depths.items()))
    msg_length = sum([d_num * freq for d_num, freq in depths.items()])
    avg_depth = msg_length / num_entries
    print("avg_depth: {0:.2f}".format(avg_depth))


def decode(reader):
    S = {}  # child -> (parent, symbol) mapping in phrase tree
    top = 0
    reader = iter(reader.read())
    while True:
        try:
            seq = get_id(reader)
        except StopIteration:
            break
        a = next(reader)
        #print("a", a)
        yield from climb_to_root(S, seq)
        yield a
        top += 1
        S[top] = (seq, a)

def get_id(reader):
    id_num = []
    while True:
        a = next(reader)
        #print("digit", a)
        if a not in "0123456789":
            return int("".join(id_num))
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
    fn = "/home/jdw/garageofcode/data/compression/nilsholg2.txt"
    #fn = "/home/jdw/garageofcode/data/compression/nilsholg.txt"
    #fn = "short.txt"
    #fn = "veryshort.txt"
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

    exit(0)

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