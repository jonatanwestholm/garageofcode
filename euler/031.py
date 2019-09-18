"""In how many ways can coins (in pence)
1, 2, 5, 10, 20, 50, 100, 200
be combined to make up the sum of 200 pence (2 pound)?
"""

def num_combs(vals, target):
    if target == 0:
        return 1
    if target < 0:
        return 0
    if not vals:
        return 0

    return num_combs(vals, target - vals[0]) + \
           num_combs(vals[1:], target)

values = [200, 100, 50, 20, 10, 5, 2, 1]
print("Num ways:", num_combs(values, 200))