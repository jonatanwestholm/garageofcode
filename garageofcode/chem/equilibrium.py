from sentian_miami import get_solver

def get_concentrations(r2c, p2k):
    """
    Get the concentrations of the reactant at equilibrium
    r2c: concentrations per reactant
    p2k: equilibrium constants per product

    products are tuples ((r0, a0), (r1, a1), ...) 
    of compounds and their correspondings cardinality, e.g

    H20 = (("H", 2), ("O", 1))
    """

    solver = get_solver("couenne")

    R = {r: solver.NumVar(lb=0, ub=1) for r in r2c}
    P = {p: solver.NumVar(lb=0, ub=1) for p in p2k}

    def get_card(p, r):
        """
        Gets the cardinality of r in p
        Returns None if r not in p
        """

        for r_i, card in p:
            if r_i == r:
                return card
        else:
            return None


    # mass balance equations
    for r, rc in R.items():
        ps = [] # parts that contain r
        for p, pc in P.items():
            for r_i, card in p:
                if r_i == r:
                    ps.append(pc * card)
                    break
        ps.append(rc) # the reactant itself
        solver.Add(solver.Sum(ps) == r2c[r])

    # reaction equilibrium equations
    for p, pc in P.items():
        rs = [] # reactant concentrations
        for r_i, card in p:
            if card == 1:
                rs.append(R[r_i])
            else:
                rs.append(R[r_i]**card)
        prod = p2k[p]
        for rc in rs:
            prod = prod * rc # don't think there is a better way
        solver.Add(prod == pc)

    solver.Solve(time_limit=10, verbose=False)

    R_solve = {r: solver.solution_value(rc) for r, rc in R.items()}
    P_solve = {p: solver.solution_value(pc) for p, pc in P.items()}

    for r, rc in R.items():
        print("{0:s}: {1:.3f}".format(r, solver.solution_value(rc)))

    #for p, pc in P.items():
    #    #print("{0:s}: {1:.3f}".format(p, solver.solution_value(pc)))
    #    print(p, solver.solution_value(pc))

    print("Total singles: {0:.3f}".format(sum(R_solve.values())))
    print("Total couples: {0:.3f}".format(sum(P_solve.values())))
