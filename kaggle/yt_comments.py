import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from garageofcode.common.utils import get_fn

def popularity_plot(df):
    popular = df[df["likes"] > 0]
    popular = popular.drop_duplicates(subset=["comment_text", "video_id"])

    plt.hist(popular["likes"], bins=np.logspace(0, 5, 30), log=True)
    plt.xscale("log")
    plt.xlabel("Likes (log10)")
    plt.ylabel("Frequency (log10)")
    plt.title("Distribution of YouTube comment popularity")

    plt.show()

def filter_popular(comments_fn, pop_comments_fn):
    df = pd.read_csv(comments_fn)

    popular = df[df["likes"] >= 100]
    contains_no_quote = ['"' not in txt for txt in popular["comment_text"]]
    popular = popular[contains_no_quote]
    tmp = popular["comment_text"].map(lambda x: '"' + x + '"')
    popular.iloc[:, 1] = tmp
    popular = popular.drop_duplicates(subset=["comment_text", "video_id"])

    popular.to_csv(pop_comments_fn)

def main():
    data_dir = get_fn(subdir="kaggle/yt_comments", main_dir="data")
    comments_fn = os.path.join(data_dir, "GBcomments.csv")
    pop_comments_fn = os.path.join(data_dir, "popular.csv")
    #filter_popular(comments_fn, pop_comments_fn)

    df = pd.read_csv(comments_fn)
    df = df.drop_duplicates(subset=["comment_text", "video_id"])

    print(np.mean(df[df["likes"] > 0]["likes"]))

    most_pop = df.nlargest(10, columns=["likes"])["comment_text"]
    for elem in most_pop:
        print(elem)
        print()
        print()


    #popularity_plot(df)


if __name__ == '__main__':
    main()