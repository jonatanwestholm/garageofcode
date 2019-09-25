import os
import numpy as np
import random
import heapq
from datetime import datetime, timedelta
from copy import copy
import networkx as nx

HRS2SEC = 3600
DAY2SEC = HRS2SEC * 24

def dbg(s, debug):
    if debug:
        print(s)

def flatten_simple(lst):
    return [elem for sublist in lst for elem in sublist]

def _flatten(l):
    try: 
        for elem in l: 
            break 
        else: 
            yield [] 
            return 
    except TypeError: 
        yield l 
        return 
    for elem in l: 
        yield from _flatten(elem) 

def flatten(l):
    return list(_flatten(l))

def transpose(l):
    return zip(*l)

def date_range(start_date, end_date):
    t = copy(start_date)
    while t <= end_date:
        yield t
        t += timedelta(days=1)

def manhattan(X, Y):
    dist = 0
    for x, y in zip(X, Y):
        dist += abs(x - y)
    return dist

def entropy(vals):
    """
    S = -sum(log2(vi/v)*vi/v)
    """
    V = sum(vals)
    return -sum(np.log2(vi/V) * vi/V if vi else 0 for vi in vals)

def print_dataframe(X, rownames=None, colnames=None, spacing=10, ignore0=True):
    if rownames is None:
        rownames = [str(i) for i in range(len(X))]
    if colnames is None:
        colnames = [str(j) for j in range(len(list(transpose(X))))]

    print(" "*spacing + "".join([colname.rjust(spacing) for colname in colnames]))
    for row, rowname in zip(X, rownames):
        print(rowname.ljust(spacing) + "".join([str(val).rjust(spacing) if val else " "*spacing for val in row]))

def power_set(a):
    """
    Takes lists only
    """
    if not a:
        yield []
    else:
        s = a[0]
        for subset in power_set(a[1:]):
            yield subset
            yield [s] + subset

def shuffled(iterable): 
    """
    Returns a generator for the elements of the
    iterable in a random order
    Warning: slow
    """
    if type(iterable) is not type([]):
        lst = list(iterable)
    else:
        lst = iterable
    N = len(lst)
    order = random.sample(range(N), N)
    for i in order:
        yield lst[i]


def get_fn(subdir, filename="", main_dir=None):
    if main_dir is None:
        main_dir = os.environ.get("GARAGEOFCODE_RESULTS", ".")
    elif main_dir == "results":
        main_dir = os.environ["GARAGEOFCODE_RESULTS"]
    elif main_dir == "data":
        main_dir = os.environ["GARAGEOFCODE_DATA"]

    dir_path = os.path.join(main_dir, subdir)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        #print("Made path:", os.path.exists(dir_path))
    else:
        pass
        #print("Path {} already exists".format(dir_path))

    if filename:
        return os.path.join(dir_path, filename)
    else:
        return dir_path


class Heap:
    """
    A heap implemented the way I want it.
    Calls to heapq lib is done behind the scenes.
    Naturally handles keys
    """
    def __init__(self, lst=None, key=None):
        if lst is None:
            lst = []
        self.key = key
        if self.key is None:
            self.h = lst
        else:
            self.h = [(self.key(elem), elem) for elem in lst]
        heapq.heapify(self.h)

    def pop(self):
        return heapq.heappop(self.h)

    def push(self, elem):
        if self.key is None:
            return heapq.heappush(self.h, elem)
        else:
            return heapq.heappush(self.h, (self.key(elem), elem))

    def __len__(self):
        return len(self.h)

def equivalence_partition(iterable, key):
    classes = []
    for item in iterable:
        for c in classes:
            c_item = next(iter(c))
            if key(c_item) == key(item):
                c.add(item)
                break
        else:
            classes.append({item})
    return classes

if __name__ == '__main__':
    h = Heap([10, 20, 6], key=lambda x: x**2)

    for i in range(5):
        h.push(i)

    N = len(h)
    for _ in range(N):
        print(h.pop())

