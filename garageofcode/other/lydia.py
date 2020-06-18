def get_lydia_points(path):
    x = 0
    y = 0
    points = set((x, y))
    for d in path:
        if d == "E":
            x += 1
        else:
            y += 1
        points.add((x, y))
    return points


T = int(input())
for case_i in range(1, T+1):
    N = int(input())
    lydia_points = get_lydia_points(input())
    path = []
    for i in range(N-1):
        if (i+1, i) in lydia_points:
            path.append("SE")
        else:
            path.append("ES")
    print("Case #{}: {}".format(case_i, "".join(path)))