def make_table(W):
    N = len(W)
    T = [0]*N
    T[0] = -1
    i = 1
    candidate = 0

    while i < N:
        print(i, candidate)
        if W[i] == W[candidate]:
            T[i] = T[candidate]
        else:
            T[i] = candidate
            while candidate >= 0 and W[i] != W[candidate]:
                candidate = T[candidate]
        i += 1
        candidate += 1
    return T

print(make_table("AABAABCAABAABCDAABAABCAABAABCDEAABAABCAABAABCDAABAABCAABAABCDEF"))