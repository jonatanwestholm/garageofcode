import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from datetime import timedelta

from common.utils import get_fn

fn = get_fn("private_tutoring_scheduling", "test_data.csv")

date_format = "%Y-%m-%d"
time_format = "%H:%M"

# Set params and generate random data
D = 5 # num days
T_D = 10 # num times per day
T = D * T_D
N = 10 # num students
max_simultaneous = [3 for _ in range(T)] # max num student per time
min_times = [1 for _ in range(N)] # min times per student
lesson_length = timedelta(minutes=20)

#available = [[random.random() < 0.1 for _ in range(T)] for _ in range(N)]

# Preference parameters
per_diem_cost = 200
time_cost = 30