import csv
from collections import defaultdict
from datetime import datetime

import garageofcode.scheduling.conf as conf

def read(fn):
    dt_format = conf.date_format + conf.time_format
    students = set()
    times = set()
    available = set()

    with open(fn, "r") as f:
        reader = csv.DictReader(f, delimiter=',')
        #reader.next() # skip header
        for row in reader:
            if not row["student_id"]:
                continue
            student = row["student_id"]
            dt = datetime.strptime(row["date"] + row["time"], dt_format)

            students.add(student)
            times.add(dt)
            available.add((student, dt))

    return students, times, available