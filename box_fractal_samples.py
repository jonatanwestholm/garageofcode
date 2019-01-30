import numpy as np

class Box:
	def __init__(self, boundaries, depth=0):
		self.boundaries = boundaries
		self.depth = depth

	def split(self):
		u = np.random.random()
		vertical = np.random.randint(2)

		x0, x1, y0, y1 = self.boundaries

		if vertical:
			mid = (x0 + x1) / 2
			bounds0 = [x0, mid, y0, y1]
			bounds1 = [mid, x1, y0, y1]
		else:
			mid = (y0 + y1) / 2
			bounds0 = [x0, x1, y0, mid]
			bounds1 = [x0, x1, mid, y1]

		return Box(bounds0, self.depth + 1), Box(bounds1, self.depth + 1)

	def sample_points(self, num_points):
		x0, x1, y0, y1 = self.boundaries
		for _ in range(num_points):
			x = x0 + (x1 - x0) * np.random.random()
			y = y0 + (y1 - y0) * np.random.random()
			yield [x, y]

def generate_points(b0, num_leafs, points_per_leaf = 1):
	boxes = [b0]
	for _ in range(num_leafs):
		b = boxes.pop(np.random.choice(len(boxes))) #, p=[2**-b.depth for b in boxes]))
		boxes.extend(b.split())

	for b in boxes:
		yield from b.sample_points(points_per_leaf)

if __name__ == '__main__':
	import matplotlib.pyplot as plt

	num_points = 1000
	points_per_leaf = 1
	points = list(generate_points(Box([0, 1, 0, 1]), num_points, points_per_leaf))

	x_coords, y_coords = zip(*points)

	plt.scatter(x_coords, y_coords)
	plt.xlabel("x")
	plt.ylabel("y")
	plt.title("{} points".format(num_points))
	plt.show()