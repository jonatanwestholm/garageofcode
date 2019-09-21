import numpy as np

from solver import get_solver

def get_data():
    N = 50
    M = 100
    A = np.random.normal(size=[N, M])
    return np.exp(A)

def main():
    min_strength = 2

    solver = get_solver("CBC")

    transmitter2receiver = get_data()

    X = [solver.IntVar(0, 1) for _ in range(len(transmitter2receiver))]

    for receiver in zip(*transmitter2receiver):
        solver.Add(solver.Dot(X, receiver) >= min_strength)

    num_transmitters = solver.Sum(X)
    solver.SetObjective(num_transmitters, maximize=False)

    solver.Solve(time_limit=10)

    X_solved = [solver.solution_value(x) for x in X]
    print(X_solved)


if __name__ == '__main__':
    main()