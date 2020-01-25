from itertools import accumulate

import numpy as np
import matplotlib.pyplot as plt

def get_exp(N):
    return np.random.exponential(scale=1.0, size=N)

def get_pol(N, alpha):
    return 1 / np.random.random(size=N)**1/alpha

def get_uni(N):
    return np.random.random(size=N)


def main():
    N = 10000
    x_exp = list(accumulate(get_exp(N), max))
    #x_uni = list(accumulate(get_uni(N), max))
    x_pol = list(accumulate(get_pol(N, 3), max))

    plt.plot(x_exp)
    plt.plot(x_pol)
    plt.show()


if __name__ == '__main__':
    main()