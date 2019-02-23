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

if __name__ == '__main__':
    #contains([1], [0, 2])
    dim2val = {0: 0.5, 1: 0.3}
    box = {0: (0, 1), 1: (0, 2), 2: (-1, 5)}

    print(profile(dim2val, [box]))
