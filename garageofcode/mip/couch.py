import numpy as np
from scipy import linalg

from babelsberg import get_solver

#p0n = np.array([-10, 0])
p0t = np.array([0, -10])
#p1n = np.array([10, -5])
#p1t = np.array([6, 8])
#p1t = np.array([5, 10])
p1t = np.array([np.sqrt(3)/2 * 10, 1/2 * 10])
g = -100 # force of gravity, N

def lp():
  solver = get_solver("couenne")

  ax = solver.num_var()
  ay = solver.num_var()
  bx = solver.num_var()
  by = solver.num_var()

  # x-forces = 0
  solver.add(ax + bx == 0)
  # y-forces = 0
  solver.add(ay + by + g == 0)

  # rotation
  solver.add(ax*p0t[0] + ay*p0t[1] + bx*p1t[0] + by*p1t[1] == 0)
  
  if 0:
    solver.add(ax == 0)
    solver.add(bx == 0)  
  else:
    #solver.set_objective(bx*bx + by*by, maximize=False)
    solver.set_objective(ax*ax + ay*ay, maximize=False)

  solver.solve(time_limit=10)

  ax_solve = solver.solution_value(ax)
  ay_solve = solver.solution_value(ay)
  bx_solve = solver.solution_value(bx)
  by_solve = solver.solution_value(by)

  print(ax_solve)
  print(ay_solve)
  print(bx_solve)
  print(by_solve)
  print(np.sqrt(ax_solve**2 + ay_solve**2))
  print(np.sqrt(bx_solve**2 + by_solve**2))

def main():
  A = np.array([[1, 0, 1, 0],
                [0, 1, 0, 1],
                [p0t[0], p0t[1], p1t[0], p1t[1]]])
  B = np.array([[0], [-g], [0]])
  #res = np.linalg.lstsq(A, B)
  res = linalg.svd(A)

  V = res[2]
  print(np.sum(V[:3], axis=0))

  '''
  res = linalg.null_space(A)
  print(res[0] / res[1])

  A = np.array([[1, 1],
                [p0t[1], p1t[1]]])
  B = np.array([[-g], [0]])
  res = np.linalg.solve(A, B)
  print(res)
  '''

if __name__ == '__main__':
  #main()
  lp()