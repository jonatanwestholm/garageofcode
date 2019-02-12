from satispy import Variable, Cnf
from satispy.solver import Minisat

def main():
	v1 = Variable('v1')
	v2 = Variable('v2')
	v3 = Variable('v3')

	exp = v1 & v2 | v3
	exp = exp & -v1
	exp = exp & -v3

	exp = Cnf.create_from(v1)
	exp = Cnf.create_from(exp)

	solver = Minisat()

	solution = solver.solve(exp)

	if solution.success:
		print(solution[v1]) #, solution[v2], solution[v3])
	else:
		print("Unsatisfiable")

if __name__ == '__main__':
	main()