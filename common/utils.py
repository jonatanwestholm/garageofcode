import numpy as np
import random
import heapq
from datetime import datetime, timedelta
from copy import copy

HRS2SEC = 3600
DAY2SEC = HRS2SEC * 24

def flatten_simple(lst):
    return [elem for sublist in lst for elem in sublist]

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

def print_dataframe(X, rownames=None, colnames=None, spacing=10, ignore0=True):
    if rownames is None:
        rownames = [str(i) for i in range(len(X))]
    if colnames is None:
        colnames = [str(j) for j in range(len(list(transpose(X))))]

    print(" "*spacing + "".join([colname.rjust(spacing) for colname in colnames]))
    for row, rowname in zip(X, rownames):
        print(rowname.ljust(spacing) + "".join([str(val).rjust(spacing) if val else " "*spacing for val in row]))

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

