def n2digits(n):
    digits = []
    i = 1
    while n:
        r = n % 10**i
        n -= r
        r = r // 10**(i-1)
        digits.append(r)
        i += 1
    return digits
    
def digits2n(digits):
    n = 0
    for i, d in enumerate(digits):
        n += d * 10**i
    return n
        
T = int(input())
for case_i in range(1, T+1):
    N = int(input())
    A = []
    B = []
    for digit in n2digits(N):
        if digit == 4:
            A.append(3)
            B.append(1)
        else:
            A.append(digit)
            B.append(0)
    #print(A)
    #print(B)
    print("Case #{}: {} {}".format(case_i, digits2n(A), digits2n(B)))