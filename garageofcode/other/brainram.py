import os
import time
from collections import Counter

import numpy as np

from garageofcode.kaggle.word2vec import get_words as get_words_list

def get_top_1000_words():
    data_dir = "/home/jdw/garageofcode/data/"
    fn = os.path.join(data_dir, "1-1000.txt")

    return [line for line in open(fn, "r").read().split()]

def get_sentences():
    fn = "/home/jdw/garageofcode/data/compression/big.txt"

    text = open(fn, "r").read()
    #text = text.replace("\n", " ")
    text = "".join([" " if ch in "\n;,:-\"" else ch for ch in text])
    text = "".join(["." if ch in "!?" else ch for ch in text])
    sentences = [sentence.strip() for sentence in text.split(".") if len(sentence.strip().split(" ")) == 15]
    return sentences

def test_category(get_items):
    while True:
        elems = get_items()
        s = "".join(["%s " %elem for elem in elems])
        line = ">> " + s
        print(line, end="\r")
        time.sleep(5)
        print(" "*100, end="\r")
        try:
            ans = input(">> ").split(" ")
        except KeyboardInterrupt:
            print()
            break
        c_elems = Counter(elems)
        c_ans = Counter(ans)
        if c_elems == c_ans:
            print("   " + s)
            print("Correct")
        else:
            print("   " + s)
        try:
            input()
        except KeyboardInterrupt:
            print()
            break
        print()


def main():
    get_ints = lambda: [str(i) for i in np.random.randint(0, 10, size=[7])]
    get_letters = lambda: [chr(i) for i in np.random.randint(97, 123, size=[7])]
    #words_list = get_words_list()
    #get_words = lambda: np.random.choice(words_list, size=[5])
    words_list_1000 = get_top_1000_words()
    get_words_1000 = lambda: np.random.choice(words_list_1000, size=[7])
    sentences = get_sentences()
    get_sentence = lambda: [np.random.choice(sentences)]
    test_category(get_sentence)

    #for i in range(10):
    #    print("line %d" %i, end="\r")
    #    time.sleep(0.5)





if __name__ == '__main__':
    main()

