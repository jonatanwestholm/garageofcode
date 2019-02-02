from utils import transpose, flatten_simple, print_dataframe
from solver import get_solver, solution_value

def main():
    solver = get_solver("CBC")

    #supply = [1, 1, 1, 1, 1]
    #demand = [1, 1, 1]

    supply = [47, 212, 140, 79, 76, 60, 91, 215, 21, 128, 250, 147]
    demand = [397, 306, 55, 257, 66, 0]

    #supply = [10, 20, 40]
    #demand = [30, 0]

    N = len(supply)
    M = len(demand)

    X = [[solver.IntVar(lb=0) for _ in range(M)] for _ in range(N)]
    Y = [[solver.IntVar(0, 1) for _ in range(M)] for _ in range(N)]
    S = [solver.IntVar(lb=0) for _ in range(N)]

    for group_assignments, size in zip(X, supply):
        solver.Add(solver.Sum(group_assignments) == size)

    for site_assigned, site_demand in zip(transpose(X), demand):
        solver.Add(solver.Sum(site_assigned) >= site_demand)

    for i in range(N):
        for j in range(M):
            solver.Add(X[i][j] <= supply[i] * Y[i][j])

    num_links = solver.Sum(flatten_simple(list(transpose(Y))[:-1]))
    #solver.SetObjective(num_links, maximize=False)
    num_workers = solver.Sum(flatten_simple(list(transpose(X))[:-1]))

    for group_links, split_group in zip(Y, S):
        solver.Add(split_group >= solver.Sum(group_links) - 1)

    num_split_groups = solver.Sum(S)
    solver.SetObjective(num_split_groups + num_workers * 0.001, maximize=False)

    solver.Solve(time_limit=10)

    print("Number of split groups:", int(solution_value(num_split_groups)))
    print("Number of used volunteers:", int(solution_value(num_workers)))
    print("Number of demanded workers:", sum(demand))

    print_dataframe([[int(solution_value(val)) for val in row] for row in X])

    print()
    print("Row sums:")
    [print(sum([int(solution_value(val)) for val in row])) for row in X]

    print()
    print("Col sums:")
    [print(sum([int(solution_value(val)) for val in col])) for col in transpose(X)]

if __name__ == '__main__':
    main()