def max_var(solver, sequence, var_type='IntVar', **kwargs):
    return _extreme_var(solver, sequence, var_type, True, **kwargs)

def min_var(solver, sequence, var_type='IntVar', **kwargs):
    return _extreme_var(solver, sequence, var_type, False, **kwargs)

def _extreme_var(solver, sequence, var_type, maximum, **kwargs):
    if var_type == 'IntVar':
        ev = solver.IntVar(**kwargs)
    elif var_type == 'NumVar':
        ev = solver.NumVar(**kwargs)

    for item in sequence:
        if maximum:
            solver.Add(ev >= item)
        else:
            solver.Add(ev <= item)

    return ev
