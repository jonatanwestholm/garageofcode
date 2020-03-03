from itertools import product
import numpy as np
import matplotlib.pyplot as plt

import networkx as nx

from garageofcode.mip.maxflow import get_flows
from garageofcode.chem.equilibrium import get_concentrations


parties = ["V", "MP", "S", "C", "L", "M", "KD", "SD"]
parties_women = [p + "w" for p in parties]
parties_men = [p + "m" for p in parties]
tolerance = np.array([[1, 1, 1, 0, 0, 0, 0, 0],
                      [1, 1, 1, 1, 1, 0, 0, 0],
                      [1, 1, 1, 1, 1, 1, 0, 0],
                      [0, 1, 1, 1, 1, 1, 1, 0],
                      [0, 1, 1, 1, 1, 1, 1, 0],
                      [0, 0, 1, 1, 1, 1, 1, 1],
                      [0, 0, 0, 1, 1, 1, 1, 1],
                      [0, 0, 0, 0, 0, 1, 1, 1],
                    ])
'''
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
'''
women_poll = {"V": 23.9, "MP": 4.9, "S": 18.0,
              "C": 16.8, "L": 4.1,
              "M": 15.1, "KD": 3.1, "SD": 11.9, }
              #"other": 2.1}

men_poll   = {"V": 8.8, "MP": 3.7, "S": 8.7,
              "C": 6.7, "L": 5.6,
              "M": 26.9, "KD": 6.1, "SD": 28.6, }
              #"other": 4.9}


def get_political_matching():
    """
    A graph that models political tolerance
    as far as dating is concerned, in Feb 2020 in Sweden. 
    Includes data from polls among women 18-29 and men 18-29.
    """

    global women_poll, men_poll

    # normalize
    women_sum = sum(women_poll.values())
    women_poll = {p: v / women_sum for p, v in women_poll.items()}
    men_sum = sum(men_poll.values())
    men_poll = {p: v / men_sum for p, v in men_poll.items()}

    '''
    # drain first order:
    first_choices = 0
    for p in parties:
        first_choice = min(women_poll[p], men_poll[p])
        first_choices += first_choice
        women_poll[p] -= first_choice 
        men_poll[p] -= first_choice 
    print("total first choice: {0:.3}".format(first_choices))
    '''

    G = nx.DiGraph()

    for p, pw, pm in zip(parties, parties_women, parties_men):
        G.add_edge("women", pw, capacity=women_poll[p])
        G.add_edge(pm, "men", capacity=men_poll[p])

    for pw, row in zip(parties_women, tolerance):
        for pm, tolerant in zip(parties_men, row):
            if tolerant:
                G.add_edge(pw, pm, capacity=1)

    return G


def get_chemical():
    """
    Dicts that model polls and equilibrium constants for couplings
    """
    global women_poll, men_poll

    # normalize
    women_sum = sum(women_poll.values()) * 2
    women_poll = {p + "w": v / women_sum for p, v in women_poll.items()}
    men_sum = sum(men_poll.values()) * 2
    men_poll = {p + "m": v / men_sum for p, v in men_poll.items()}

    r2c = {}
    r2c.update(women_poll)
    r2c.update(men_poll)

    p2c = {((pw, 1), (pm, 1)): 4900 for (i, pw), (j, pm) in 
            product(enumerate(parties_women), enumerate(parties_men))
                if tolerance[i][j]}

    return r2c, p2c


def visualize(G, flows):
    # mostly hard code

    total_flow = sum([flows[e] for e in G.in_edges("men")])
    #print("Total flow: {0:.3f}".format(total_flow))

    node2coord = {"women": (0, 0), "men": (3, 0),
                  "Vw": (1, 3.5), "MPw": (1, 2.5), "Sw": (1, 1.5), "Cw": (1, 0.5),
                  "Lw": (1, -0.5), "Mw": (1, -1.5), "KDw": (1, -2.5), "SDw": (1, -3.5),
                  "Vm": (2, 3.5), "MPm": (2, 2.5), "Sm": (2, 1.5), "Cm": (2, 0.5),
                  "Lm": (2, -0.5), "Mm": (2, -1.5), "KDm": (2, -2.5), "SDm": (2, -3.5),
                  }

    for node, (x, y) in node2coord.items():
        plt.scatter(x, y, c='b')
        plt.text(x, y, node)

    for (u, v), flow in sorted(flows.items(), key=lambda x: x[1]):
        if not (u == "women" or v == "men"):
            flow = 0.05
            color = "k"
            #print(u, v, "{0:.3f}".format(flow))
        else:
            color = "r"

        #if not flow:
        #    continue
        ux, uy = node2coord[u]
        vx, vy = node2coord[v]
        plt.plot([ux, vx], [uy, vy], color=color, linewidth=10*np.abs(flow), zorder=0)

    #plt.title("Total match rate: {0:.1f}%".format(total_flow*100))
    plt.axis("off")

    plt.show()


def get_left_out(G, flows):
    for node in G:
        if node[-1] == "w":
            total_capacity = sum(G.edges[e]["capacity"] for e in G.in_edges(node))
        elif node[-1] == "m":
            total_capacity = sum(G.edges[e]["capacity"] for e in G.out_edges(node))
        else:
            continue
        total_flow = sum(flows[e] for e in G.in_edges(node))
        left_out = (total_capacity - total_flow) / total_capacity
        print("{0:s}: {1:.1f}%".format(node, left_out*100))
        #print("{0:s}: {1:.1f}%\n".format(node, total_capacity*100))


def network_flow_model():
    G = get_political_matching()
    flows = get_flows(G, "women", "men", capacity="capacity")
    get_left_out(G, flows)
    #visualize(G, flows)


def chemical_model():
    r2c, p2k = get_chemical()
    get_concentrations(r2c, p2k)


def main():
    chemical_model()


if __name__ == '__main__':
    main()