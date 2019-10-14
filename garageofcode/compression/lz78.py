import os
from collections import defaultdict
#import networkx as nx

splitter = " "

def encode(reader):
    G = defaultdict(dict)  # phrase tree
    seq = 0  # sequence id
    top = 0  # highest id in use
    for a in reader.read():
        seq_old = seq
        try:
            seq = G[seq][a]
        except KeyError:
            yield seq, a
            top += 1
            G[seq][a] = top  # extend tree
            seq = 0  # restart at root
    if seq:
        yield seq_old, a

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
    for a in reversed(stack):
        yield a

def main():
    fn = "/home/jdw/garageofcode/data/compression/nilsholg.txt"
    #fn = "short.txt"
    fn_compressed = fn.split(".")[0] + ".wzip"
    fn_reconstructed = fn.split(".")[0] + "_rec.txt"
    # encoding step
    with open(fn, "r") as r:
        with open(fn_compressed, "w") as f:
            for seq, a in encode(r):
                #if a == "\n":
                #    f.write("{}{}\\n".format(seq, splitter))
                #else:
                f.write("{}{}{}".format(seq, splitter, a))
    print("Before ", os.stat(fn).st_size)
    print("After  ", os.stat(fn_compressed).st_size)

    with open(fn_compressed, "r") as r:
        with open(fn_reconstructed, "w") as f:
            for a in decode(r):
                if a == "\\n":
                    f.write("\n")
                else:
                    f.write(a)

    res = os.system("diff {} {}".format(fn, fn_reconstructed))
    if res:
        print("Reconstruction: failed")
    else:
        print("Reconstruction: OK")

if __name__ == '__main__':
    main()