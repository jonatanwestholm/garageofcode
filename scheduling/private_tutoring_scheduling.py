import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import random
from collections import defaultdict, OrderedDict
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from common.utils import transpose, flatten_simple, equivalence_partition, DAY2SEC
from mip.solver import get_solver, solution_value, status2str
from mip.miputils import max_var, min_var
from scheduling.read import read
import scheduling.conf as conf

def constraint_take_times(solver, students, student_time2take, take_times):
    for student in students:
        takes = [take for (st_id, _), take in student_time2take.items() if st_id == student]
        solver.Add(solver.Sum(takes) == take_times[student])

def constraint_max_simultaneous(solver, times, student_time2take, max_simultaneous):
    for dt in times:
        takes = [take for (_, t), take in student_time2take.items() if t == dt]
        solver.Add(solver.Sum(takes) <= max_simultaneous[dt])

def get_total_workdays(solver, times, student_time2take):
    day2takes = []
    for day in equivalence_partition(times, lambda x: x.date()):
        takes = [take for (_, t), take in student_time2take.items() if t in day]
        day2takes.append(takes)

    works_days = [solver.IntVar(0, 1) for _ in day2takes]

    for works_day, takes in zip(works_days, day2takes):
        for take in takes:
            solver.Add(works_day >= take)

    return solver.Sum(works_days), works_days

def get_total_time_span(solver, times, student_time2take):
    day2start_time = {}
    day2end_time = {}
    day2time_span = {}
    for day in equivalence_partition(times, lambda x: x.date()):
        date = next(iter(day))
        midnight = datetime.combine(date, date.time())

        day_takes = [(t, take) for (_, t), take in student_time2take.items() if t in day]

        busy_times = []
        for dt in equivalence_partition(day, lambda x: x.time()):
            t_of_d = (next(iter(dt)) - midnight).total_seconds()
            busy = max_var([take for t, take in day_takes if t in dt], lb=0, ub=1)
            busy_times.append(t_of_d * busy)

        start_time = min_var(busy_times, 'NumVar', lb=0, ub=DAY2SEC)
        end_time = max_var(busy_times, 'NumVar', lb=0, ub=DAY2SEC)

        day2start_time[date] = start_time
        day2end_time[date] = end_time
        day2time_span = end_time - start_time

    return solver.Sum(day2time_span.Values()), day2start_time, day2end_time

def draw_tutoring_schedule(ax, student_time2take, available, D, T_D):
    T = D * T_D
    N = len(student_time2take) + 1
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
    for student, time2take in enumerate(student_time2take):
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

def draw_teacher_schedule(ax, student_time2take, st_d, et_d, D, T_D):
    T = D * T_D

    time2student2take = list(transpose(student_time2take))

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

    student_time2take = dict([(item, solver.IntVar(0, 1)) for item in available])

    # Add constraints
    constraint_take_times(solver, students, student_time2take, take_times)
    constraint_max_simultaneous(solver, times, student_time2take, max_simultaneous)

    # Add costs and values
    obj = 0
    total_workdays, works_days = get_total_workdays(solver, times, student_time2take)
    obj -= total_workdays * per_diem_cost
    total_time, st_d, et_d = get_total_time_span(solver, student_time2take, D, T_D)
    obj -= total_time * time_cost

    solver.SetObjective(obj, maximize=True)

    status = solver.Solve(time_limit=10)
    print(status2str[status])
    if status2str[status] not in ["OPTIMAL", "FEASIBLE"]:
        return

    student_time2take_solve = [[solution_value(take) for take in time2take] 
                                            for time2take in student_time2take]
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
    draw_tutoring_schedule(ax, student_time2take_solve, available, D, T_D)
    draw_teacher_schedule(ax, student_time2take_solve, st_d_solve, et_d_solve, D, T_D)
    #plt.axis("off")
    title = ["Total nbr workdays: {}".format(total_workdays_solve),
             "Total time: {}".format(total_time_solve)]
    plt.title("\n".join(title))
    plt.show()

if __name__ == '__main__':
    main()