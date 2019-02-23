import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import numpy as np
import matplotlib.pyplot as plt

def white_noise(y, std):
	return y + np.random.normal()*std



def main():
	N = 1000
	transition = lambda y: white_noise(y, 1)

	y = []
	yt = 0

	for _ in range(N):
		y.append(yt)
		yt = transition(yt)

	y_prev, y_post = y[:-1], y[1:]

	fig, ax = plt.subplots(ncols=2)
	ax_series, ax_scatter = ax

	ax_series.plot(y)
	ax_series.set_xlabel("Iteration")
	ax_series.set_ylabel("Value")
	ax_series.set_title("Series")

	ax_scatter.scatter(y_prev, y_post)
	ax_scatter.set_xlabel("y(t-1)")
	ax_scatter.set_ylabel("y(t)")
	ax_scatter.set_title("Transitions")

	plt.show()

if __name__ == '__main__':
	main()