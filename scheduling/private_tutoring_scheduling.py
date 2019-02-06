import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import random
from collections import defaultdict, OrderedDict
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from common.utils import transpose, flatten_simple
from mip.solver import get_solver, solution_value, status2str
from scheduling.read import read
import scheduling.conf as conf

def make_take_times_constraint(solver, student2time2take, take_times):
    for student, time2take in student2time2take.items():
        solver.Add(solver.Sum(time2take.Values()) == take_times[student])
    
def make_max_simultaneous_constraint(solver, student2time2take, max_simultaneous):
    student2time2take_matrix = [[elem for dt, take in time2take.items()] 
                        for student, time2take in student2time2take.items()]
    for time, student2take in enumerate(transpose(student2time2take)):
        solver.Add(solver.Sum(student2take) <= max_simultaneous[time])

def make_availability_constraint(solver, student2time2take, available):
    for student, time2take in enumerate(student2time2take):
        for time, take in enumerate(time2take):
            solver.Add(take <= available[student][time])

def get_total_workdays(solver, student2time2take, D, T_D):
    works_days = [solver.IntVar(0, 1) for _ in range(D)]

    time2student2take = list(transpose(student2time2take))

    for d, works_day in enumerate(works_days):
        student2take = time2student2take[d*T_D:(d+1)*T_D]
        student2take = flatten_simple(student2take)
        for take in student2take:
            solver.Add(works_day >= take)

    return solver.Sum(works_days), works_days

def get_total_time_span(solver, student2time2take, D, T_D):
    start_time_day = [solver.NumVar(lb=0, ub=T_D-1) for _ in range(D)]
    end_time_day = [solver.NumVar(lb=0, ub=T_D-1) for _ in range(D)]
    #end_time_day = [1 for _ in range(D)]

    time2student2take = list(transpose(student2time2take))

    for d, (start_time, end_time) in enumerate(zip(start_time_day, end_time_day)):
        for t_of_d in range(T_D):
            t = d * T_D + t_of_d
            any_take = solver.IntVar(0, 1)
            for take in time2student2take[t]:
                solver.Add(any_take >= take)
            #any_take = 1
            solver.Add(start_time <= any_take * (t_of_d) + (1 - any_take) * T_D)
            solver.Add(end_time >= any_take * t_of_d)

    time_span_day = [et - st for st, et in zip(start_time_day, end_time_day)]

    return solver.Sum(time_span_day), start_time_day, end_time_day

def draw_tutoring_schedule(ax, student2time2take, available, D, T_D):
    T = D * T_D
    N = len(student2time2take) + 1
    # Draw time and date lines
    for y in range(N + 1):
        if y == 1:
            linewidth = 3 # teacher's line
        else:
            linewidth = 1
        ax.plot([0, T], [y, y], c='k', linewidth=linewidth)

    for x in range(T + 1):
        if x % T_D == 0:
            linewidth = 3 # date line
        else:
            linewidth = 1
        ax.plot([x, x], [0, N], c='k', linewidth=linewidth)

    # Draw student's schedules and available
    for student, time2take in enumerate(student2time2take):
        for time, take in enumerate(time2take):
            #print(student, time)
            if take:
                patch = Rectangle((time, student + 1), 1, 1, facecolor='b')
            elif available[student][time]:
                patch = Rectangle((time, student + 1), 1, 1, facecolor='b', alpha=0.3)
            else:
                continue
            ax.add_patch(patch)

    ax.set_yticks([elem + 0.5 for elem in range(N)])
    ax.set_yticklabels(["Teacher"] + ["Student {}".format(i+1) for i in range(N-1)])

    ax.set_xticks(range(T_D // 2, T, T_D))
    ax.set_xticklabels(["Day {}".format(i+1) for i in range(D)])

def draw_teacher_schedule(ax, student2time2take, st_d, et_d, D, T_D):
    T = D * T_D

    time2student2take = list(transpose(student2time2take))

    for d in range(D):
        for t_of_d in range(T_D):
            t = d * T_D + t_of_d
            if sum(time2student2take[t]) > 0:
                patch = Rectangle((t, 0), 1, 1, facecolor='b')
            elif st_d[d] <= t_of_d and t_of_d < et_d[d]:
                patch = Rectangle((t, 0), 1, 1, facecolor='r', alpha=0.3)
            else:
                continue
            ax.add_patch(patch)

def main():
    students, times, available = read(conf.fn)

    take_times = dict([(student, 1) for student in students])
    max_simultaneous = dict([(dt, 3) for dt in times])

    # Generate variables
    solver = get_solver("CBC")

    student2time2take = OrderedDict([(student, OrderedDict([(dt, solver.IntVar(0, 1)) for student in sorted(times)])) 
                                                                                        for id in sorted(students)])

    # Add constraints
    make_availability_constraint(solver, student2time2take, available)
    make_min_times_constraint(solver, student2time2take, take_times)
    make_max_simultaneous_constraint(solver, student2time2take, max_simultaneous)

    # Add costs and values
    obj = 0
    total_workdays, works_days = get_total_workdays(solver, student2time2take, D, T_D)
    obj -= total_workdays * per_diem_cost
    total_time, st_d, et_d = get_total_time_span(solver, student2time2take, D, T_D)
    obj -= total_time * time_cost

    solver.SetObjective(obj, maximize=True)

    status = solver.Solve(time_limit=10)
    print(status2str[status])
    if status2str[status] not in ["OPTIMAL", "FEASIBLE"]:
        return

    student2time2take_solve = [[solution_value(take) for take in time2take] 
                                            for time2take in student2time2take]
    st_d_solve = [int(solution_value(st)) for st in st_d]
    et_d_solve = [int(solution_value(et)) for et in et_d]

    #print(st_d_solve)
    #print(et_d_solve)

    works_days_solve = [int(solution_value(wd)) for wd in works_days]

    #print(works_days_solve)

    total_workdays_solve = int(solution_value(total_workdays))
    #total_time_solve = int(solution_value(total_time))
    total_time_solve = sum([(et - st + 1)*wd for st, et, wd in 
                            zip(st_d_solve, et_d_solve, works_days_solve)])

    fig, ax = plt.subplots()
    draw_tutoring_schedule(ax, student2time2take_solve, available, D, T_D)
    draw_teacher_schedule(ax, student2time2take_solve, st_d_solve, et_d_solve, D, T_D)
    #plt.axis("off")
    title = ["Total nbr workdays: {}".format(total_workdays_solve),
             "Total time: {}".format(total_time_solve)]
    plt.title("\n".join(title))
    plt.show()

if __name__ == '__main__':
    main()