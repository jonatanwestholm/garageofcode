from pysat.solvers import Glucose4

class GlucoseRush(Glucose4):

	def __init__(self):
		super().__init__()
		self.var_num = 0

	def var(self):
		self.var_num += 1
		return self.var_num

def main():
	g = GlucoseRush()

	a = g.var()
	b = g.var()

	g.add_clause([-a, b])

	g.solve()
	print(g.get_model())

if __name__ == '__main__':
	main()