import os

import numpy as np
import matplotlib.pyplot as plt

import pandas as pd

data_dir = "/home/jdw/projects/kaggle/data/city_lines/"

def get_df(fn):
    path = os.path.join(data_dir, fn+".csv")
    return pd.read_csv(path)

def pointstr2coord(pointstr):
    pointstr = pointstr[6:-1]
    x, y = pointstr.split(" ")
    return np.array([float(x), float(y)])

def main():
    # ciites, lines, tracks, track_lines, stations, station_lines, systems

    cities = get_df("cities")
    stations = get_df("stations")

    city_id2name = {cid: name for cid, name in zip(cities["id"], cities["name"])}
    city_id2country = {cid: name for cid, name in zip(cities["id"], cities["country"])}

    #print(city_id2name[29])
    # budapest: 29
    # stockholm: 110
    stations = stations[stations["city_id"] == 110]
    #print(len(stations))

    points = stations["geometry"].map(pointstr2coord)
    for elem in sorted(stations["name"]):
        print(elem)

    dist = np.array([[np.linalg.norm(p0 - p1) for p1 in points] for p0 in points])

    plt.imshow(dist < 0.001)
    plt.show()



if __name__ == '__main__':
    main()