import numpy as np 
import pandas as pd

def main():
    df = pd.read_csv("/home/jdw/garageofcode/data/kaggle/food/FAO.csv", delimiter=",")

    df_item = df[["sugar" in item.lower() and element == "Food"
                    for item, element in zip(df["Item"], df["Element"])]].groupby("Area")["Y2013"].sum().sort_values(ascending=False)
    print(df_item.head(20))


if __name__ == '__main__':
    main()