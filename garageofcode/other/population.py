import numpy as np
import matplotlib.pyplot as plt

def child_mortality():
  N = 200 # total pop
  k = int(N * 0.1) # initial bearers
  T = 100 # generations per simulation
  M = 1000 # total simulations

  bx = 0.1
  x = 0.05 # mortality
  g = 0.0 # reduced-mortality factor

  failed = 0

  for _ in range(M):
    pop = [0]*(N - k) + [1]*k
    ratios = []
    for _ in range(T):
      new_pop = []
      # vitality
      for org in pop:
        if org and np.random.rand() < (1 - bx - g * x):
          new_pop.append(org)
        if not org and np.random.rand() < (1 - bx - x):
          new_pop.append(org)

      pop = new_pop

      # doubling pop
      pop = pop * 2

      pop = np.random.permutation(pop)
      pop = pop[:N]

      r = np.mean(pop)
      ratios.append(r)
      if r == 0:
        failed += 1
        break
      if r == 1:
        break

    plt.plot(ratios)

  print("failed rate:", failed/M)

  plt.show()

def crisis():
  N = 200 # total pop
  k = int(N * 0.02) # initial bearers
  T = 100 # generations per simulation
  M = 100 # total simulations

  x = 0.1 # mortality
  g = 0.9 # reduced-mortality factor
  c = 0.2 # crisis likelihood per year
  y = 20 # years per generation

  failed = 0

  for _ in range(M):
    pop = [0]*(N - k) + [1]*k
    ratios = []
    for _ in range(T):
      new_pop = []
      # vitality
      num_crises = np.sum(np.random.rand(y) < c)
      for org in pop:
        if org and np.random.rand() < (1 - g * x) ** num_crises:
          new_pop.append(org)
        if not org and np.random.rand() < (1 - x) ** num_crises:
          new_pop.append(org)

      pop = new_pop

      # doubling pop
      pop = pop * 2

      pop = np.random.permutation(pop)
      pop = pop[:N]

      r = np.mean(pop)
      ratios.append(r)
      if r == 0:
        failed += 1
        break
      if r == 1:
        break

    plt.plot(ratios)

  print("failed rate:", failed/M)
  plt.show()

if __name__ == '__main__':
  #crisis()
  child_mortality()