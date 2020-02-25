import numpy as np

import networkx as nx

from garageofcode.mip.maxflow import get_flows

def get_political_matching():
    """
    A graph that models political tolerance
    as far as dating is concerned, in Feb 2020 in Sweden. 
    Includes data from polls among women 18-29 and men 18-29.
    """

    parties = ["V", "MP", "S", "C", "L", "M", "KD", "SD", "other"]
    parties_women = [p + "w" for p in parties]
    parties_men = [p + "m" for p in parties]
    tolerance = np.array([[1, 1, 1, 0, 0, 0, 0, 0, 0],
                          [1, 1, 1, 1, 1, 0, 0, 0, 0],
                          [1, 1, 1, 1, 1, 1, 0, 0, 0],
                          [0, 1, 1, 1, 1, 1, 1, 0, 0],
                          [0, 1, 1, 1, 1, 1, 1, 0, 0],
                          [0, 0, 1, 1, 1, 1, 1, 1, 0],
                          [0, 0, 0, 1, 1, 1, 1, 1, 0],
                          [0, 0, 0, 0, 0, 1, 1, 1, 1],
                          [1, 0, 0, 0, 0, 0, 0, 0, 0],
                        ])
    women_poll = {"V": 23.9, "MP": 4.9, "S": 18.0,
                  "C": 16.8, "L": 4.1,
                  "M": 15.1, "KD": 3.1, "SD": 11.9, 
                  "other": 2.1}

    men_poll   = {"V": 8.8, "MP": 3.7, "S": 8.7,
                  "C": 6.7, "L": 5.6,
                  "M": 26.9, "KD": 6.1, "SD": 28.6,
                  "other": 4.9}


    # normalize
    women_sum = sum(women_poll.values())
    women_poll = {p: v / women_sum for p, v in women_poll.items()}
    men_sum = sum(men_poll.values())
    men_poll = {p: v / men_sum for p, v in men_poll.items()}

    G = nx.DiGraph()

    for p, pw, pm in zip(parties, parties_women, parties_men):
        G.add_edge("women", pw, capacity=women_poll[p])
        G.add_edge(pm, "men", capacity=men_poll[p])

    for pw, row in zip(parties_women, tolerance):
        for pm, tolerant in zip(parties_men, row):
            if tolerant:
                G.add_edge(pw, pm, capacity=100)

    return G


def main():
    G = get_political_matching()
    get_flows(G, "women", "men", capacity="capacity")


if __name__ == '__main__':
    main()