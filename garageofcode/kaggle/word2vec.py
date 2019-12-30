import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from garageofcode.tda.main import get_mds

def get_words():
        data_dir = "/home/jdw/garageofcode/data/kaggle/word2vec_sample"
        fn = os.path.join(data_dir, "pruned.word2vec.txt")
        
        df = pd.read_csv(fn, delimiter=",", nrows=None)

        words = df["word"]
        words = words.map(lambda x: x.lower())

        return words.drop_duplicates()

class Word2Vec:
    def __init__(self, fn):
        df = pd.read_csv(fn, delimiter=",", nrows=None)

        df.iloc[:, 0] = df.iloc[:, 0].map(lambda x: x.lower())
        df = df.drop_duplicates(subset="word")

        self.word2id = {word.lower(): i for i, word in enumerate(df.iloc[:, 0])}
        self.id2word = {i: word.lower() for i, word in enumerate(df.iloc[:, 0])}
        self.id2vec = np.array(df.iloc[:, 1:].applymap(float))

    def direct_output(func):
        def wrapper_output(self, *args, **kwargs):
            if "output" in kwargs:
                output = kwargs["output"]
            else:
                output = kwargs.get("pipe_nearest", False)
            res = func(self, *args, **kwargs)
            if output:
                kwargs["n_out"] = kwargs.get("n_out", 10)
                kwargs["ignore"] = kwargs.get("ignore", args)
                self.print_nearest(res, **kwargs)
            else:
                return res
        return wrapper_output

    def print_nearest(self, nearest, ignore=[], n_out=10, hypothesis=None, **kwargs):
        for idx, (a, i) in enumerate(nearest[:n_out]):
            s = self.id2word[i]
            if s in ignore:
                continue
            print("{2:d} {0:s}: {1:.3f}".format(s, a, idx+1))
        if hypothesis:
            print()
            for idx, (a, i) in enumerate(nearest):
                s = self.id2word[i]
                if s == hypothesis:
                    print("{2:d} {0:s}: {1:.3f}".format(s, a, idx+1))
                    break

    def pipe_nearest(pipe=True):
        def meta(func):
            def wrapper_pipe(self, *args, **kwargs):
                do_pipe = kwargs.get("pipe_nearest", pipe)
                res = func(self, *args, **kwargs)
                if do_pipe:
                    return self.get_nearest(res)
                else:
                    return res
            return wrapper_pipe
        return meta

    def get_nearest(self, vec):
        alignment = np.dot(self.id2vec, vec)
        alignment = [(a, i) for i, a in enumerate(alignment)]
        nearest = list(sorted(alignment, reverse=True))
        return nearest

    def __call__(self, word):
        return self.word2vec(word)

    @pipe_nearest(pipe=False)
    def word2vec(self, word, **kwargs):
        vec = self.id2vec[self.word2id[word]]
        vec = vec / np.linalg.norm(vec)
        return vec

    @direct_output
    @pipe_nearest()
    def reduce(self, head, words, **kwargs):
        """
        if we remove the part of head that are similar to words,
        what remains?
        """

        vec_head = self.word2vec(head)
        vecs = [self.word2vec(word) for word in words]
        return self.reduce_vec(vec_head, vecs)

    def reduce_vec(self, vec_head, vecs):
        for vec in vecs:
            vec_head = self.reduce_single(vec_head, vec)
        vec_head = vec_head / np.linalg.norm(vec_head)
        return vec_head

    def reduce_single(self, vec_head, vec_word):
        '''
        return vec_head - vec_word
        '''
        norm = np.linalg.norm(vec_word)
        a = np.dot(vec_head, vec_word) / norm
        vec_head = vec_head - vec_word * a
        return vec_head

    @direct_output
    @pipe_nearest()
    def analogy(self, head0, tail0, head1, **kwargs):
        """
        what is related to head1 as head0 is related to tail0?

        assumption:
        head0 - tail0 = head1 - tail1

        example:
        london - england = tokyo - japan
        """

        vec_head0 = self.word2vec(head0)
        vec_tail0 = self.word2vec(tail0)
        vec_head1 = self.word2vec(head1)

        vec_tail1 = vec_head1 - vec_head0 + vec_tail0
        return vec_tail1

    @direct_output
    def alignment(self, head, words, **kwargs):
        vec_head = self.word2vec(head)
        vecs = [(self.word2vec(word), self.word2id[word]) 
                for word in words]
        return list(sorted([(np.dot(vec_head, vec), i) for vec, i in vecs], reverse=True))

    @direct_output
    @pipe_nearest()
    def relation(self, head, rel, **kwargs):
        """
        what has the relation rel to head?

        assumption:
        head - tail = rel

        example:

        london - england = capital
        """

        vec_head = self.id2vec[self.word2id[head]]
        vec_rel = self.id2vec[self.word2id[rel]]

        vec_tail = vec_head - vec_rel
        return vec_tail

    @direct_output
    @pipe_nearest()
    def hypernym(self, words, hypothesis=None, **kwargs):
        """
        what word best describes this class?
        """

        vecs = np.array([self.id2vec[self.word2id[word]] for word in words])
        vec_avg = np.mean(vecs, axis=0)
        return vec_avg

def graph_mds(X, annotations=None):
    """Make the best attempt att projecting
    to a 2D plane
    """
    metric = np.dot
    X_transformed, _ = get_mds(X, metric, dim=2)

    xcoords, ycoords = zip(*X_transformed)

    fig, ax = plt.subplots()

    ax.scatter(xcoords, ycoords)

    if annotations is not None:
        for ann, x, y in zip(annotations, xcoords, ycoords):
            ax.annotate(ann, (x, y))

    plt.show()


def main():
    data_dir = "/home/jdw/garageofcode/data/kaggle/word2vec_sample"
    fn = os.path.join(data_dir, "pruned.word2vec.txt")
    #id2word, word2id, id2vec = get_word2vec(fn)
    w2v = Word2Vec(fn)

    #w2v.reduce("london", ["england"], output=True)

    #N = 1000
    #graph_mds(w2v.id2vec[:N], annotations=[w2v.id2word[i] for i in range(N)])
    words = ["london", "england",
             "berlin", "germany",
             "rome", "italy",
             "paris", "france",
             "tokyo", "japan", 
             "copenhagen", "denmark",
             "moscow", "russia",
             "madrid", "spain",
             "istanbul", "turkey",
             "oslo", "norway",
             "vienna", "austria",
             "budapest", "hungary"
             ]
    graph_mds([w2v.word2vec(word) for word in words], words)


    #print(id2word)
    #print(word2id)

    #nearest = get_nearest("family", word2id, id2vec)
    #nearest = analogy("book", "library", "tree", word2id, id2vec)  # should yield 'forest'
    #nearest = relation("tree", "many", word2id, id2vec) # should yield 'forest'
    #nearest = hyponym(["memoir", "novel", "textbook"], word2id, id2vec) # should yield 'book'
    #nearest = hyponym(["mother", "father", "brother", "sister"], word2id, id2vec) # should yield 'family'


    '''
    for a, i in nearest[:10]:
        print("{0:s}: {1:.3f}".format(id2word[i], a))
    '''



if __name__ == '__main__':
    main()