from sat.solver import SugarRush

def allowed_cards(solver, variables, cardinalities):
    bounds = [solver.equals(variables, bound=card) for card in cardinalities]
    return solver.disjunction(bounds)

def get_covering(coord, coord2tiles):
    incident_tiles = []
    incident_coords = []
    x, y = coord
    #print(coord)
    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
        neigh = (x+dx, y+dy)
        if neigh in coord2tiles:
            incident_tiles.append(coord2tiles[neigh])
            incident_coords.append(neigh)
    #print(incident_coords)
    return incident_tiles

def rokicki16_solve(board, num_moves):
    solver = SugarRush()

    coord2tiles = dict((coord, solver.var()) for coord in sorted(board))

    coord2covering = dict((coord, get_covering(coord, coord2tiles)) for coord in board)

    evens = list(range(0, num_moves+1, 2))
    odds  = list(range(1, num_moves+1, 2))
    for coord, val in board.items():
        covering = coord2covering[coord]
        #print(coord)
        if val:
            parity_bound = allowed_cards(solver, covering, odds)
        else:
            parity_bound = allowed_cards(solver, covering, evens)
        solver.add(parity_bound)

    tile_vars = list(coord2tiles.values())
    total_moves_bound = solver.equals(tile_vars, bound=num_moves)
    solver.add(total_moves_bound)

    satisfiable = solver.solve() #assumptions=[-1, -2, -3, -4, 5, -6, -7, -8, -9])
    print("Satisfiable:", satisfiable)
    if not satisfiable:
        return {}

    return dict((coord, solver.solution_value(tile)) for coord, tile in coord2tiles.items())

def rokicki16():
    num_moves = 7
    board = [[1, 0, 0, 0, 0],
             [1, 0, 1, 1, 0],
             [0, 1, 1, 1, 1],
             [0, 0, 1, 1, 0],
             [0, 0, 1, 1, 1]]
    #board = [[1]]
    #board = [[0, 1, 0],
    #         [1, 1, 1],
    #         [0, 1, 0],]
    N = len(board)
    M = len(board[0])
    board_dict = {}
    for i, row in enumerate(board):
        for j, val in enumerate(row):
            board_dict[(i, j)] = val
    print(board_dict)

    coord2val = rokicki16_solve(board_dict, num_moves)
    if not coord2val:
        return

    coord2covering = dict((coord, get_covering(coord, coord2val)) for coord in board_dict)

    for i in range(N):
        print(", ".join([str(coord2val[(i, j)]) for j in range(M)]))

    print()

    for i in range(N):
        print(", ".join([str((board_dict[(i, j)] + sum(coord2covering[(i, j)])) % 2) for j in range(M)]))