import time
from collections import Counter

import numpy as np

from garageofcode.kaggle.word2vec import get_words as get_words_list

def test_category(get_items):
    while True:
        elems = get_items()
        s = "".join(["%s " %elem for elem in elems])
        line = ">> " + s
        print(line, end="\r")
        time.sleep(5)
        print(" "*100, end="\r")
        ans = input(">> ").split(" ")
        c_elems = Counter(elems)
        c_ans = Counter(ans)
        if c_elems == c_ans:
            print("   " + s)
            print("Correct")
        else:
            print("   " + s)
        input()
        print()

def main():
    get_ints = lambda: [str(i) for i in np.random.randint(0, 10, size=[7])]
    get_letters = lambda: [chr(i) for i in np.random.randint(97, 123, size=[7])]
    words_list = get_words_list()
    get_words = lambda: np.random.choice(words_list, size=[5])
    test_category(get_words)

    #for i in range(10):
    #    print("line %d" %i, end="\r")
    #    time.sleep(0.5)





if __name__ == '__main__':
    main()

