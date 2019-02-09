import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import numpy as np
import random
from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta
from datetime import time as midnight_time
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from common.utils import transpose, flatten_simple, equivalence_partition, date_range, DAY2SEC
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

def get_day2works(solver, times, student_time2take):
    day2works = {}
    for day in equivalence_partition(times, lambda x: x.date()):
        date = next(iter(day)).date()
        takes = [take for (_, t), take in student_time2take.items() if t in day]
        works = max_var(solver, takes, lb=0, ub=1)
        day2works[date] = works

    return day2works

def get_day2time_span(solver, times, student_time2take):
    day2start_time = {}
    day2end_time = {}
    day2time_span = {}
    for day in equivalence_partition(times, lambda x: x.date()):
        dt0 = next(iter(day))
        midnight = datetime.combine(dt0.date(), midnight_time())
        date = dt0.date()

        day_takes = [(t, take) for (_, t), take in student_time2take.items() if t in day]

        start_busy_times = []
        end_busy_times = []
        busy_times = []
        for dt in equivalence_partition(day, lambda x: x.time()):
            t_of_d = (next(iter(dt)) - midnight).total_seconds()
            takes = [take for t, take in day_takes if t in dt]
            busy = max_var(solver, takes, lb=0, ub=1)
            start_busy_times.append(busy * t_of_d + (1 - busy) * DAY2SEC)
            end_busy_times.append(busy * t_of_d)
            busy_times.append(busy)

        busy_at_all = [solver.Sum(busy_times) * DAY2SEC]
        start_time = min_var(solver, start_busy_times + busy_at_all, 'NumVar', lb=0, ub=DAY2SEC)
        end_time = max_var(solver, end_busy_times, 'NumVar', lb=0, ub=DAY2SEC)

        day2start_time[date] = start_time
        day2end_time[date] = end_time
        day2time_span[date] = (end_time - start_time) / 3600.0

    return day2time_span

def draw_tutoring_schedule(ax, students, times, student_time2take):
    students = list(sorted(students))
    T = len(times)
    N = len(students) + 1 # plus the teacher

    day_classes = equivalence_partition(times, lambda x: x.date())
    dates = [next(iter(d_c)).date() for d_c in day_classes]
    dts = [datetime.combine(date, midnight_time()) for date in dates]
    min_dt = min(dts)
    max_dt = max(dts)+timedelta(days=1)
    for dt in date_range(min_dt, max_dt):
        ax.plot([dt, dt], [0, N], c='k', linewidth=3)

    for y in range(N + 1):
        if y == 1:
            linewidth = 3 # teacher's line
        else:
            linewidth = 1
        ax.plot([min_dt, max_dt], [y, y], c='k', linewidth=linewidth)

    # Draw student's schedules
    for (student, dt), take in student_time2take.items():
        st_idx = students.index(student) + 1
        if take:
            patch = Rectangle((dt, st_idx), conf.lesson_length, 1, facecolor='b', zorder=1)
        else: # just available
            patch = Rectangle((dt, st_idx), conf.lesson_length, 1, facecolor='b', alpha=0.3, zorder=0)
        ax.add_patch(patch)

    ax.set_yticks([elem + 0.5 for elem in range(N)])
    ax.set_yticklabels(["Teacher"] + ["Student {}".format(i+1) for i in range(N-1)])

def draw_teacher_schedule(ax, times, student_time2take):
    for day in equivalence_partition(times, lambda x: x.date()):
        day_times = [t for (_, t), take in student_time2take.items() if t in day and take]
        if not len(day_times):
            continue

        st = min(day_times)
        et = max(day_times)

        patch = Rectangle((st, 0), et-st, 1, facecolor='r', alpha=0.3)
        ax.add_patch(patch)

        for t in day_times:
            patch = Rectangle((t, 0), conf.lesson_length, 1, facecolor='b')
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
    obj = solver.NumVar(lb=0, ub=0)
    day2works = get_day2works(solver, times, student_time2take)
    obj -= solver.Sum(day2works.values()) * conf.per_diem_cost
    day2t_s = get_day2time_span(solver, times, student_time2take)
    obj -= solver.Sum(day2t_s.values()) * conf.time_cost

    solver.SetObjective(obj, maximize=True)

    status = solver.Solve(time_limit=10)
    print(status2str[status])
    if status2str[status] not in ["OPTIMAL", "FEASIBLE"]:
        return 0
    print(int(np.around(solution_value(obj))))

    student_time2take_solve = dict([(key, solution_value(take)) 
                                for key, take in student_time2take.items()])

    day2works_solve = dict([(key, solution_value(take)) 
                            for key, take in day2works.items()])

    day2t_s_solve = dict([(key, solution_value(take))
                            for key, take in day2t_s.items()])
    
    total_days = int(sum(day2works_solve.values()))
    lesson_length_hrs = conf.lesson_length.total_seconds() / 3600
    total_time = sum(day2t_s_solve.values()) + total_days * lesson_length_hrs
    fig, ax = plt.subplots()
    draw_tutoring_schedule(ax, students, times, student_time2take_solve)
    draw_teacher_schedule(ax, times, student_time2take_solve)
    title = ["Total nbr workdays: {0:d}".format(total_days),
             "Total time: {0:.2f} h".format(total_time)]
    plt.title("\n".join(title))
    plt.show()

if __name__ == '__main__':
    main()