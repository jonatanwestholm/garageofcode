import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from common.utils import get_fn

tape = {}
head = 0
state = "b"

def R():
    global head
    head += 1

def L():
    global head
    head -= 1

def P(sym):
    tape[head] = sym

def read(tmp=None):
    if tmp is None:
        return tape.get(head, None)
    else:
        return tape.get(tmp, None)

def error(val):
    print("\nError")
    debug(val)
    exit(1)

def debug(val):
    print("Tape:")
    print_full_tape()
    print("Head:", head)
    print("State:", state)
    print("Val:", val)
    print()

def print_full_tape():
    print(", ".join([str((i, sym)) for i, sym in sorted(tape.items())]))

def print_tape():
    print(", ".join([str(sym) for i, sym in sorted(tape.items()) if i % 2 == 0]))

def draw_tape(ax):
    max_len = 13
    ax.clear()
    for idx in range(max_len):
        patch = Rectangle((idx, 0), 1, 1, fill=False)
        ax.add_patch(patch)

        sym = read(idx)
        sym = sym if sym is not None else ""
        if sym in [0, 1]:
            col = "r"
        else:
            col = "b"
        ax.text(idx + 0.3, 0.3, sym, color=col)

    patch = Rectangle((head, 0), 1, 1, fill=False, color="g", linewidth=5)
    ax.add_patch(patch)

    ax.set_xlim([0, max_len])
    ax.set_aspect("equal")
    ax.axis("off")
    plt.draw()
    plt.pause(0.01)

def main():
    save_dir = get_fn("turing/gif")
    fig, ax = plt.subplots(figsize=(15, 1))
    idx = 0
    while not accumulating():
        draw_tape(ax)
        path = os.path.join(save_dir, "{0:04d}.png".format(idx))
        plt.savefig(path)
        #print("idx:", idx)
        #debug(read())
        if idx == 1000:
            print_tape()
            break
        else:
            idx += 1

def alternating():
    global state
    if state == 0:
        R()
        R()
        P(0)
        state = 1
    elif state == 1:
        R()
        R()
        P(1)
        state = 0
    else:
        return True
    return False

def accumulating():
    global state
    val = read()
    if state == "b":
        P("e"), R(), P("e"), R(), P(0), R(), R(), P(0), L(), L()
        state = "a"
    elif state == "a":
        if val == 1:
            R(), P("x"), L(), L(), L()
            state = "a"
        elif val == 0:
            state = "q"
        else:
            error(val)
    elif state == "q":
        if val in [0, 1]:
            R(), R()
            state = "q"
        elif val is None:
            P(1), L()
            state = "p"
        else:
            error(val)
    elif state == "p":
        if val == "x":
            P(None), R()
            state = "q"
        elif val == "e":
            R()
            state = "s"
        elif val is None:
            L(), L()
            state = "p"
        else:
            error(val)
    elif state == "s":
        if val is None:
            P(0), L(), L()
            state = "a"
        else:
            R(), R()
            state = "s"
    else:
        error(-1)

if __name__ == '__main__':
    main()