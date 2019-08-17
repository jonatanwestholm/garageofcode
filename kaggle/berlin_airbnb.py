import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection

import pandas as pd

def price_map(fn):
    df = pd.read_csv(fn)
    reasonable = df["price"].between(1, 200)
    longitude = df["longitude"][reasonable]
    latitude = df["latitude"][reasonable]
    price = df["price"][reasonable]

    print(len(price))

    plt.scatter(longitude, latitude, c=price)
    plt.colorbar()
    plt.show()


def price_map_binned(df, aggregator="min", fig=None, ax=None):
    longs = (13.05, 13.8)
    lats = (52.3, 52.7)
    #df = pd.read_csv(listings_fn)
    #available = df["availability_365"] >= 200
    #df = df[available]
    price_range = df["price"].between(1, 200)
    #print("Num listings:", len(df))
    df = df[price_range]    
    x_grid = np.linspace(*longs)
    y_grid = np.linspace(*lats)
    long_bins = pd.cut(df["longitude"], x_grid)
    lat_bins = pd.cut(df["latitude"], y_grid)
    bins = long_bins.combine(lat_bins, func=lambda x, y: (x, y))
    tile_means = df.groupby(bins)["price"].agg([aggregator])

    patches = []
    prices = []

    for (xg, yg), price in zip(tile_means.index.values, tile_means[aggregator]):
        x0, x1 = xg.left, xg.right
        y0, y1 = yg.left, yg.right
        rect = Rectangle((x0, y0), width=x1-x0, height=y1-y0)
        patches.append(rect)
        prices.append(price)

    if fig is None:
        fig, ax = plt.subplots()
    p = PatchCollection(patches)
    p.set_array(np.array(prices))
    ax.add_collection(p)
    #fig.colorbar(p, ax=ax)
    ax.set_xlim(longs)
    ax.set_ylim(lats)

    ax.set_xlabel("longitude")
    ax.set_ylabel("latitude")
    ax.set_title("Berlin AirBnB listings Nov 2018-Nov 2019\nAggregated by {} price".format(aggregator))


def date_price_map(listings_fn, availability_fn):
    df = pd.read_csv(availability_fn)
    df = df[df["available"] == "t"]
    df["price"] = df["price"].map(lambda x: float(x[1:].replace(",", "")))
    df.sort_values("date")
    date_groups = df.groupby("date")

    listings = pd.read_csv(listings_fn)
    id2long = {id_num: lng for id_num, lng in zip(listings["id"], listings["longitude"])}
    id2lat = {id_num: lat for id_num, lat in zip(listings["id"], listings["latitude"])}

    fig, ax = plt.subplots()
    aggregator = "mean"

    for date_listings in date_groups:
        date = date_listings[0]
        date_listings = pd.DataFrame(date_listings[1])
        date_listings["longitude"] = date_listings["listing_id"].map(id2long)
        date_listings["latitude"] = date_listings["listing_id"].map(id2lat)
        price_map_binned(date_listings, fig=fig, ax=ax, aggregator=aggregator)
        ax.set_title("{0:s} price, {1:s}".format(aggregator, date))
        plt.pcolor(vmin=1, vmax=200)
        plt.draw()
        plt.pause(0.1)
        ax.cla()


def price_timeline(availability_fn):
    aggregator = "mean"
    df = pd.read_csv(availability_fn, nrows=10000)
    df = df[df["available"] == "t"]
    df["price"] = df["price"].map(lambda x: float(x[1:].replace(",", "")))
    #df.sort_values("date")
    date_groups = df.groupby("date")
    #cheapest = date_groups["price"].agg([aggregator])
    quantiles = [0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
    quants = [date_groups["price"].quantile(q) for q in quantiles]

    for quant in quants:
        plt.step(quant.index.values, quant)
    plt.xticks(quants[0].index.values[::7], rotation="45")
    #plt.title("The {} AirBnB price in Berlin over time".format(aggregator))
    plt.title("Quantiles of AirBnB price in Berlin over time")
    plt.legend(quantiles)
    plt.xlabel("date")
    plt.ylabel("USD")
    plt.show()


def main():
    data_dir = "/home/jdw/projects/kaggle/data/berlin_airbnb/"
    listings_fn = os.path.join(data_dir, "listings.csv")
    availability_fn = os.path.join(data_dir, "calendar_summary.csv")
    #price_map_binned(listings_fn)
    #date_price_map(listings_fn, availability_fn)
    price_timeline(availability_fn)


if __name__ == '__main__':
    main()