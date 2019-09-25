import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima_process import ArmaProcess

def poles(k):
    """
    Generates k pairs of poles in the unit circle
    Returns the resulting polynomial coefficients
    """

    pol = np.array([1])
    for _ in range(k):
        theta = np.random.random()*np.pi
        r = np.random.random()**0.5 # to get uniform over area
        coeffs = np.array([1, -2*np.cos(theta)*r, r**2])

        pol = np.convolve(pol, coeffs) # polynomial multiplication

    return pol

def get_ts(N, p=0, q=0):
    return ArmaProcess(poles(p), poles(q)).generate_sample(N)

def main():
    ar = poles(5)
    #coeffs = -coeffs[1:] # Y = 1/(1 - p(z^-1)) => Y = p(z^-1)Y
    ma = poles(0)

    ps = ArmaProcess(ar, ma)
    y = ps.generate_sample(1000)

    plt.plot(y)
    plt.title("Example AR process")
    plt.xlabel("t")
    plt.ylabel("y")
    plt.show()


if __name__ == '__main__':
    main()