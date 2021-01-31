import numpy as np

from sentian_miami import get_solver

def minimize_circumference():
    """Minimize the circumference
    of all rectangle with a minimal area.
    The answer should of course be a square.
    """

    solver = get_solver("couenne")

    x = solver.NumVar(0, 5)
    y = solver.NumVar(0, 5)
    z = 2 * (x + y)

    solver.Add(x * y >= 9)
    solver.SetObjective(z, maximize=False)

    solver.Solve()

    print("x:", solver.solution_value(x))
    print("y:", solver.solution_value(y))
    print("z:", solver.solution_value(z))

def compress_piecewise(x_data, y_data):
    N = len(x_data)
    redundant = []

    for idx in range(N-2):
        x0, x1, x2 = x_data[idx+0], x_data[idx+1], x_data[idx+2]
        y0, y1, y2 = y_data[idx+0], y_data[idx+1], y_data[idx+2]

        if (x1 - x0) * (y2 - y0) == (x2 - x0) * (y1 - y0):
            redundant.append(idx + 1)

    return [xi for idx, xi in enumerate(x_data) if idx not in redundant],\
           [yi for idx, yi in enumerate(y_data) if idx not in redundant]

def single_row():
    
    solver = get_solver("couenne")
    #solver.solver.options["tol"] = 1e-7
    #solver.solver.options["display_stat"] = "yes"

    #f = np.array([-1, 10, -10])
    f = np.random.normal(size=[10])
    #f = np.array([0, 1, -1, 0])
    width = len(f)
    xl_data = list(range(width + 1))
    yl_data = [0] + list(np.cumsum(f))
    sum_f = yl_data[-1]

    #xl_data, yl_data = compress_piecewise(xl_data, yl_data)
    #print("len x_data after compress:", len(xl_data))

    xr_data = xl_data
    yr_data = list(sum_f - np.array(yl_data))

    #print(xl_data, yl_data)
    #print(xr_data, yr_data)

    xl = solver.NumVar(0, width)
    xr = solver.NumVar(0, width)

    solver.Add(xl <= xr)

    yl, constr_l = solver.Piecewise(xl, xl_data, yl_data)
    yr, constr_r = solver.Piecewise(xr, xr_data, yr_data)

    solver.SetObjective(yl + yr, maximize=False)

    solver.Solve()

    print("xl: {0:.3f}".format(solver.solution_value(xl)))
    print("yl: {0:.3f}".format(solver.solution_value(yl)))
    print("xr: {0:.3f}".format(solver.solution_value(xr)))
    print("yr: {0:.3f}".format(solver.solution_value(yr)))

    print("SOS2_y L:")
    print([float("{0:.2f}".format(solver.solution_value(val))) for key, val in constr_l.SOS2_y.items()])
    print("SOS2_y R:")
    print([float("{0:.2f}".format(solver.solution_value(val))) for key, val in constr_r.SOS2_y.items()])
    #print(solver.solution_value(constr_l.SOS2_y[0]))

if __name__ == '__main__':
    #minimize_circumference()
    #max_operator()
    single_row()