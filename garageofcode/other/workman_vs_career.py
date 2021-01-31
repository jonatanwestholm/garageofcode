import numpy as np
from collections import deque

def propagate(a, children, N):
    for _ in range(N):
        a_new = sum([a[ch] for ch in children]) / 2.0
        a.popleft()
        a.append(a_new)
    return a

def main():
    a_workman = deque([1]*9)
    children_workman = [0, 1, 2]

    a_career = deque([1]*14)
    children_career = [0, 1, 2, 3]

    N = 30 # 90 years

    b_workman = propagate(a_workman, children_workman, N)
    b_career = propagate(a_career, children_career, N)

    print("b_workman:", np.mean(b_workman))
    print("b_career: ", np.mean(b_career))

    # conclusion: expedience does not matter very much (for humans),
    # having one more child is more fit, even if it means waiting 
    # about 10 years before starting to have children

    # Of course, in practice, most people who have children
    # later in life also have fewer children. So it is 
    # kind of a false tradeoff. 

if __name__ == '__main__':
    main()