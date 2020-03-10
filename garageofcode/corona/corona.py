import os
from datetime import datetime, timedelta

import numpy as np
import matplotlib.pyplot as plt

import pandas as pd

from sentian_miami import get_solver

line_data_dir = "/home/jdw/garageofcode/data/kaggle/corona/"
data_dir = "/home/jdw/repositories/COVID-19/csse_covid_19_data/csse_covid_19_time_series/"
res_dir = "/home/jdw/garageofcode/results/corona/"
num_cases_data = os.path.join(data_dir, "time_series_19-covid-Confirmed.csv")
case_data = os.path.join(line_data_dir, "COVID19_open_line_list.csv")

"""
latest = {"Sweden": 248, "Norway": 205, "Italy": 9172,
            "France": 1209, "Germany": 1176, "UK": 321, 
            "Netherlands": 321, "Belgium": 239, "Spain": 1073,
            "Switzerland": 374, "Iran": 7161, "Japan": 511,
            "South Korea": 7478, "Singapore": 150, 
            "Mainland China": 80735, "US": 604}
"""
latest = {}

def exponential_regression(cases):
    N = len(cases)
    A = np.ones([N, 2])
    A[:, 0] = list(range(N))
    b = np.log(cases)
    res = np.linalg.lstsq(A, b, rcond=None)
    alpha, beta = res[0]
    alpha = np.exp(alpha)
    beta = np.exp(beta)
    return alpha, beta

def get_num_confirmed(country):
    df = pd.read_csv(num_cases_data)

    df = df[df["Country/Region"] == country].sum()
    days = [datetime.strptime(date, "%m/%d/%y") for date in df.keys()[4:]]
    last_day = max(days)
    if country in latest:
        val = latest[country]
        today = last_day + timedelta(hours=24)
        today = datetime.strftime(today, "%m/%d/%y")
        df.at[today] = val * 1.0
    return df.iloc[4:]

def case_trend():
    for country in ["Sweden", "US", "France", "Germany", "Italy", 
                    "Iran", "UK", "South Korea", "Netherlands", 
                    "Norway", "Belgium", "Spain", "Switzerland", 
                    "Japan", "Singapore"]:
        #df_country = df[df["Country/Region"] == country]
        #print(df)
        #day2case = df_country.groupby(["ObservationDate"])["Confirmed"].sum()
        day2case = get_num_confirmed(country)
        day2case = day2case[day2case >= 70]
        #print(min((day2case.keys())))
        days = [datetime.strptime(date, "%m/%d/%y") for date in day2case.keys()]
        #last_day = max(days.keys())

        #exit(0)
        #print(len(df_swe))

        #d0 = datetime(2020, 2, 27)
        #dt = timedelta(hours=24)
        #data = np.array([2, 2, 7, 12, 14, 15, 21, 35, 94, 101, 161, 203])
        data = day2case.to_numpy()
        data = np.array([val for val in data]) # mysteriously breaks without this
        #if country in latest:
        #    data = list(data)
        #    data.append(latest[country])
        #    data = np.array(data)
        #times = [d0 + dt * i for i in range(len(data))]
        times_arr = np.array(range(len(data)))

        alpha, beta = exponential_regression(data)
        #print(alpha, beta)

        plt.scatter(times_arr, data)
        plt.semilogy(times_arr, data)
        plt.semilogy(times_arr, beta * alpha**times_arr, c="r")
        #plt.xticks(rotation=30)
        #plt.yticks([0, 1, 2, 3], [1, 10, 1000])
        plt.xlabel("Days since {}".format(datetime.strftime(min(days), "%Y-%m-%d")))
        plt.title("Cases in {}".format(country))
        plt.legend(["data", "{0:.2f} * {1:.2f}^t".format(beta, alpha)])
        #plt.show()

        plt.savefig(os.path.join(res_dir, "{}.png".format(country)))
        plt.close()


def get_do_dc(df):
    dos = []
    dcs = []

    num_errors = 0

    for do, dc in zip(df["date_onset_symptoms"], df["date_confirmation"]):
        try:
            do = datetime.strptime(do, "%d.%m.%Y")
            dc = datetime.strptime(dc, "%d.%m.%Y")
        except TypeError as e:
            print("do:", do)
            print("dc:", dc)
            raise e
        except ValueError as e:
            #print("ValueError")
            #print("do:", do)
            #print("dc:", dc)
            #print()
            num_errors += 1
            continue

        dos.append(do)
        dcs.append(dc)

    #print("Number of row errors:", num_errors)

    return dos, dcs


def get_delay2freq():
    df = pd.read_csv(case_data)
    df = df.dropna(subset=["date_onset_symptoms", "date_confirmation"])
    country2ncases = df.groupby("country").size()
    #print(country2ncases)
    #exit(0)
    date_onsets, date_conf = get_do_dc(df)
    diff = np.array([(dc - do).total_seconds() / (3600 * 24) 
                        for do, dc in zip(date_onsets, date_conf) if dc >= do])
    '''
    plt.hist(-diff, bins=2*int(max(diff)))
    plt.title("N={}\n(China 455, Japan 135, Singapore 69, South Korea 21, Others 54)".format(len(diff)))
    plt.xlabel("Days from onset to confirmation")
    plt.ylabel("Cases")
    plt.show()
    '''
    print("Median:", np.median(diff))

    delay2freq, _ = np.histogram(diff, bins=int(max(diff)))
    return delay2freq


def estimate_unconfirmed():
    for country in ["Singapore", "Sweden", "US", "France", "Germany", "Italy", 
                    "Iran", "UK", "South Korea", "Netherlands", 
                    "Norway", "Belgium", "Spain", "Switzerland", 
                    "Japan", "Mainland China"]:
        #df_country = df[df["Country/Region"] == country]
        #day2case = df_country.groupby(["ObservationDate"])["Confirmed"].sum()
        day2case = get_num_confirmed(country)
        #day2case = day2case[day2case >= 70]
        days = [datetime.strptime(date, "%m/%d/%y") for date in day2case.keys()]

        total_confirmed = day2case.to_numpy()
        times_arr = np.array(range(len(total_confirmed)))

        cutoff_days = 14
        delay2freq = get_delay2freq()
        delay2freq = delay2freq[:cutoff_days] # two weeks cutoff
        delay2freq = delay2freq / np.sum(delay2freq) # normalize
        delay2freq = delay2freq[::-1]
        #plt.plot(delay2freq)
        #plt.show()

        new_confirmed = np.diff(total_confirmed)
        #new_confirmed = new_confirmed[:-28]
        N = len(new_confirmed)
        A = np.zeros([N, N + cutoff_days - 1])
        for i in range(N):
            A[i, i:i+cutoff_days] = delay2freq

        #plt.imshow(A)
        #plt.show()

        solver = get_solver("couenne")

        new_cases = [solver.NumVar(lb=0) for _ in range(N + cutoff_days)]
        errs = []
        for row, new_conf in zip(A, new_confirmed):
            est_confirmed = solver.Sum([nc * elem for elem, nc in zip(row, new_cases)])
            err = solver.NumVar(lb=0)
            err = (est_confirmed - new_conf)**2
            # absolute error
            #solver.Add(err >= est_confirmed - new_conf)
            #solver.Add(err >= new_conf - est_confirmed)
            errs.append(err)
        total_err = solver.Sum(errs)

        total_cases = [solver.Sum(new_cases[:i+1]) for i in range(N + cutoff_days)]
        total_cases = total_cases[cutoff_days-1:]
        print(len(total_confirmed), len(total_cases))
        for tn_conf, tn_case in zip(total_confirmed, total_cases):
            solver.Add(tn_case >= tn_conf)

        #mass: baseline hypothesis is that number of new cases is 0
        #mass = solver.Sum(nc for nc in new_cases)        
        mass_sq = solver.Sum(nc**2 for nc in new_cases)
        
        #diff: baseline hypothesis is that number of new cases is like yesterday
        #diff = solver.Sum([(nc1 - nc0)**2 for nc0, nc1 in zip(new_cases, new_cases[1:])])
        
        #exp_diff: baseline hypothesis is that number of new cases grow by 30% each day
        #exp_diff = solver.Sum([(nc1 - 1.3 * nc0)**2 for nc0, nc1 in zip(new_cases, new_cases[1:])])


        solver.SetObjective(total_err + mass_sq * 0.1, maximize=False)
        solver.Solve(time_limit=10, verbose=False)

        new_cases_solve = [solver.solution_value(nc) for nc in new_cases]
        total_cases = np.cumsum(new_cases_solve)

        plt.plot(range(cutoff_days - 1, N + cutoff_days), total_confirmed, c="b")
        plt.plot(range(N + cutoff_days), total_cases, c="r")
        plt.title("Estimated best case unconfirmed {}".format(country))
        plt.xlabel("Days")
        plt.legend(["Confirmed cases", "Estimated total incl. unconfirmed"])
        plt.savefig(os.path.join(res_dir, "est_unconfirmed/unconfirmed_{}.png".format(country)))
        plt.close()


if __name__ == '__main__':
    #case_trend()
    get_delay2freq()
    #estimate_unconfirmed()














