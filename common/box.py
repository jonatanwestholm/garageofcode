import numpy as np
from itertools import product
import networkx as nx

class hashabledict(dict):
    def __key(self):
        return tuple(sorted(self.items()))

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.__key() == other.__key()

class Box(hashabledict):
    """
    Multi dimensional closedopen intervals
    Dimensions can be any hashable

    Possible future features:
    - Accept single value as dim2val
    - Support different kinds of intervals (open, closed, openclosed)
    - Prevent mutating dict
    """
    def __init__(self, dim2ij, force_order=False):
        dim2ij = self.autodict(dim2ij)
        for dim, ij in dim2ij.items():
            if not len(ij):
                self[dim] = ()
            else:
                i, j = ij
                self[dim] = (i, j)
        if force_order:
            if not self.is_ordered():
                self.clear()

    def autodict(self, dim2val):
        # if dim2val not dict, assume dim=idx
        if isinstance(dim2val, dict):
            return dim2val
        else:
            return {dim: val for dim, val in enumerate(dim2val)}

    def is_ordered(self):
        """
        Checks if all interval edges are ordered
        from left to right
        """
        for (i, j) in self.values():
            if i > j:
                return False
        else:
            return True

    def order(self):
        """
        Orders all dimensions from left to right
        """
        dims = list(self.keys())
        for dim in dims:
            ij = self[dim]
            if not len(ij):
                continue
            i, j = ij
            i1 = min(i, j)
            j1 = max(i, j)
            self[dim] = (i1, j1)

    def volume(self):
        """
        Ignores order
        Empty dimensions nullify volume
        """
        vol = 1
        for dim, ij in self.items():
            if not len(ij):
                return 0
            i, j = ij
            vol *= np.abs(j - i)
        return vol

    def corners(self):
        return product(*self.values())

    def contains(self, dim2val):
        dim2val = self.autodict(dim2val)
        for dim, val in dim2val.items():
            if dim not in self:
                return False
            ij = self[dim]
            if not len(ij):
                return False
            i, j = ij
            if val < i or j <= val:
                return False
        return True

    def contains_profile(self, dim2val):
        """
        contains when the value has infinite span in some 
        dimensions
        """
        dim2val = self.autodict(dim2val)
        for dim, val in dim2val.items():
            i, j = self[dim]
            if val < i or j <= val:
                return False
        return True

    def profile(self, dim2val):
        """
        Returns the expansion of the box in the 
        dimensions missing from dim2val
        """
        dim2val = self.autodict(dim2val)
        if not self.contains_profile(dim2val):
            return {}
        return {d: (i, j) for d, (i, j) in self.items() 
                if d not in dim2val}

    def tuple_2(self):
        return ((i, j) for d, (i, j) in sorted(self.items()))

    @staticmethod
    def intersection(b0, b1):
        dims = list(b0.keys()) + list(b1.keys())
        intersect = {}
        for dim in dims:
            if dim not in self:
                return Box({})
            if dim not in other:
                return Box({})
            c0 = self[dim]
            c1 = self[dim]
            c = Box.intersection1d(c0, c1)
            if not c:
                return Box({})
            intersect[dim] = c
        return Box(intersect)

    @staticmethod
    def intersection1d(c0, c1):
        i0, j0 = c0
        i1, j1 = c1

        i, j = max(i0, i1), min(j0, j1)
        if i < j:
            return (i, j)
        else:
            return ()

class BoxTree(nx.DiGraph):
    def copy(self):
        return nx.DiGraph.copy(self)

    def get_leafs(self):
        return [v for v, d in self.out_degree() if d == 0]
    
    def num_leafs(self):
        return len(self.get_leafs())

    def get_root(self):
        for node, deg in self.in_degree():
            if deg == 0:
                return node
        else:
            print("Found no root!")

    def profile(self, dim2val):
        """
        Returns leafs of T that overlap with dim2val,
        projected onto the dimensions that are not specified in dim2val
        """
        stack = [self.get_root()]
        while stack:
            box = stack.pop()
            if box.contains_profile(dim2val):
                if not self[box]: # found a leaf
                    yield box
                for child in self[box]:
                    stack.append(child)

    def remove_subtree(self, node): 
        """
        Assumes directed tree
        Giving it an undirected tree will remove all nodes
        """
        remove_stack = [node]
        num_removed = 1
        while remove_stack:
            n = remove_stack.pop()
            for child in self[n]:
                remove_stack.append(child)
            self.remove_node(n)
            num_removed += 1
        return num_removed

'''
def contains(x, box):
    if len(x) != len(box):
        msg = "Dimension mismatch {} vs. {}".format(len(x), len(box))
        raise ValueError(msg)
    for xi, (i, j) in zip(x, box):
        if xi < i or j < xi:
            return False
    return True

def profile_d(x_d, dim, boxes):
    """
    projects boxes onto x[dim] == x_d,
    if they overlap
    """
    projected = []
    for box in boxes:
        (i, j) = box[dim]
        if i <= x_d and x_d <= j:
            proj_box = {d: (i, j) for d, (i, j) in box.items() if d != dim}
            projected.append(proj_box)
    return projected

def profile(dim2val, boxes):
    """
    Collapses dimension dim to value dim2val[dim]
    Example:
    dim2val = {0: 0.5, 1: 0.3}
    box = {0: (0, 1), 1: (0, 2), 2: (-1, 5)}
    Returns {2: (-1, 5)}
    Returns only boxes that overlap with dim2val
    """
    for dim, x_d in dim2val.items():
        boxes = profile_d(x_d, dim, boxes)
    return boxes

def get_corners(box):
    boundaries = [(i, j) for dim, (i, j) in sorted(box.items())]
    return product(*boundaries)
'''

if __name__ == '__main__':
    #contains([1], [0, 2])
    dim2val = {0: 0.5, 1: 0.3}
    dim2ij = {0: (0, 1), 1: (0, 2), 2: (-1, 5)}
    box = Box(dim2ij)

    print(box.profile(dim2val))
    #print(list(get_corners(box)))
