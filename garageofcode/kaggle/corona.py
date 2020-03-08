import os
from datetime import datetime, timedelta

import numpy as np
import matplotlib.pyplot as plt

import pandas as pd

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


def main():
    fn_dir = "/home/jdw/garageofcode/data/kaggle/corona/"
    fn = os.path.join(fn_dir, "covid_19_data.csv")

    df = pd.read_csv(fn)

    for country in ["Sweden", "US", "France", "Germany", "Italy", 
                    "Iran", "UK", "South Korea", "Netherlands", 
                    "Norway", "Belgium", "Spain", "Switzerland", "Japan"]:
        df_country = df[df["Country/Region"] == country]
        #print(df)
        day2case = df_country.groupby(["ObservationDate"])["Confirmed"].sum()
        day2case = day2case[day2case >= 70]
        #print(min((day2case.keys())))
        days = [datetime.strptime(date, "%m/%d/%Y") for date in day2case.keys()]

        #exit(0)
        #print(len(df_swe))

        #d0 = datetime(2020, 2, 27)
        #dt = timedelta(hours=24)
        #data = np.array([2, 2, 7, 12, 14, 15, 21, 35, 94, 101, 161, 203])
        data = day2case.to_numpy()
        #times = [d0 + dt * i for i in range(len(data))]
        times_arr = np.array(range(len(data)))

        alpha, beta = exponential_regression(data)
        #print(alpha, beta)

        plt.semilogy(times_arr, data)
        plt.semilogy(times_arr, beta * alpha**times_arr, c="r")
        #plt.xticks(rotation=30)
        #plt.yticks([0, 1, 2, 3], [1, 10, 1000])
        plt.xlabel("Days since {}".format(datetime.strftime(min(days), "%Y-%m-%d")))
        plt.title("Cases in {}".format(country))
        plt.legend(["data", "{0:.2f} * {1:.2f}^t".format(beta, alpha)])
        #plt.show()

        plt.savefig("/home/jdw/garageofcode/results/kaggle/corona/{}.png".format(country))
        plt.close()


if __name__ == '__main__':
    main()