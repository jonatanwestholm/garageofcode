
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


