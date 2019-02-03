import numpy as np
import random
import heapq

def flatten_simple(lst):
    return [elem for sublist in lst for elem in sublist]

def transpose(l):
    return zip(*l)

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
	"""
	lst = list(iterable)
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
	def __init__(self, lst=[], key=None):
		self.key = key
		if self.key is None:
			self._h = lst
		else:
			self._h = [(self.key(elem), elem) for elem in lst]
		heapq.heapify(self._h)

	def pop(self):
		return heapq.heappop(self._h)

	def push(self, elem):
		if self.key is None:
			return heapq.heappush(self._h, elem)
		else:
			return heapq.heappush(self._h, (self.key(elem), elem))

	def __len__(self):
		return len(self._h)

if __name__ == '__main__':
	h = Heap([10, 20, 6], key=lambda x: x**2)

	for i in range(5):
		h.push(i)

	N = len(h)
	for _ in range(N):
		print(h.pop())

