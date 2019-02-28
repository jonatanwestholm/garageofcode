def interval_contains2(c, p): # exclusive
    ix, jx, iy, jy = c
    px, py = p
    return ix <= px < jx and iy <= py < jy

def get_corners2(c):
    ix, jx, iy, jy = c
    return [(ix, iy), 
            (ix, jy), 
            (jx, jy),
            (jx, iy)] 

def get_area2(c):
    ix, jx, iy, jy = c    
    for x in range(ix, jx):
        for y in range(iy, jy):
            yield (x, y)

def interval_overlap2(c0, c1):
    if any([interval_contains2(c0, p) for p in get_area2(c1)]):
        return True
    if any([interval_contains2(c1, p) for p in get_area2(c0)]):
        return True
    return False

def intersection(c0, c1):
    i0, j0 = c0
    i1, j1 = c1

    i, j = max(i0, i1), min(j0, j1)
    if i < j:
        return (i, j)
    else:
        return ()