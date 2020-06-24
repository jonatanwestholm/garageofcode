def get_all_nums(sn):
    for i in range(len(sn) + 1):
        yield int("".join(sn[:i] + ["5"] + sn[i:]))

def solution2(N):
    is_negative = N < 0

    sn = list(str(N))
    if is_negative:
        sn = sn[1:]

    if is_negative:
        return -min(get_all_nums(sn))
    else:
        return max(get_all_nums(sn))

def solution(N):
    is_negative = N < 0
    
    sn = list(str(N))
    if is_negative:
        sn = sn[1:]
    
    if not is_negative:
        for i, digit in enumerate(map(int, sn)):
            if digit < 5:
                break
        else:
            i += 1
    else:
        for i, digit in enumerate(map(int, sn)):
            if digit > 5:
                break
        else:
            i += 1
            
    sn = sn[:i] + ["5"] + sn[i:]
        
    if is_negative:
        sn = ["-"] + sn
        
    return int("".join(sn))

'''
for N in range(-9000, 9000):
    if solution(N) != solution2(N):
        print(N)
        break
'''

print(solution(-999))