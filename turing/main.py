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

def read():
    return tape.get(head, None)

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

def print_tape(tape):
    print(", ".join([str(sym) for i, sym in sorted(tape.items()) if i % 2 == 0]))

def main():
    idx = 0
    while not accumulating():
        #print("idx:", idx)
        #debug(read())
        if idx == 1000:
            print_tape(tape)
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