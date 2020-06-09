import time
import numpy as np
import matplotlib.pyplot as plt

import pandas as pd
import networkx as nx
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

categorical = {
               "MOSTYPE",  
               #"MGEMLEEF",  # let this be numerical instead
               "MOSHOOFD", 
               #"MGODRK" # let this be numerical
              }

L = {
        "MOSTYPE": "Customer Subtype see L0",
        "MAANTHUI": "Number of houses 1 - 10",
        "MGEMOMV": "Avg size household 1 - 6",
        "MGEMLEEF": "Avg age see L1",
        "MOSHOOFD": "Customer main type see L2",
        "MGODRK": "Roman catholic see L3",
        "MGODPR": "Protestant ...",
        "MGODOV": "Other religion",
        "MGODGE": "No religion",
        "MRELGE": "Married",
        "MRELSA": "Living together",
        "MRELOV": "Other relation",
        "MFALLEEN": "Singles",
        "MFGEKIND": "Household without children",
        "MFWEKIND": "Household with children",
        "MOPLHOOG": "High level education",
        "MOPLMIDD": "Medium level education",
        "MOPLLAAG": "Lower level education",
        "MBERHOOG": "High status",
        "MBERZELF": "Entrepreneur",
        "MBERBOER": "Farmer",
        "MBERMIDD": "Middle management",
        "MBERARBG": "Skilled labourers",
        "MBERARBO": "Unskilled labourers",
        "MSKA": "Social class A",
        "MSKB1": "Social class B1",
        "MSKB2": "Social class B2",
        "MSKC": "Social class C",
        "MSKD": "Social class D",
        "MHHUUR": "Rented house",
        "MHKOOP": "Home owners",
        "MAUT1": "1 car",
        "MAUT2": "2 cars",
        "MAUT0": "No car",
        "MZFONDS": "National Health Service",
        "MZPART": "Private health insurance",
        "MINKM30": "Income < 30.000",
        "MINK3045": "Income 30-45.000",
        "MINK4575": "Income 45-75.000",
        "MINK7512": "Income 75-122.000",
        "MINK123M": "Income >123.000",
        "MINKGEM": "Average income",
        "MKOOPKLA": "Purchasing power class",
        "PWAPART": "Contribution private third party insurance see L4",
        "PWABEDR": "Contribution third party insurance (firms) ...",
        "PWALAND": "Contribution third party insurane (agriculture)",
        "PPERSAUT": "Contribution car policies",
        "PBESAUT": "Contribution delivery van policies",
        "PMOTSCO": "Contribution motorcycle/scooter policies",
        "PVRAAUT": "Contribution lorry policies",
        "PAANHANG": "Contribution trailer policies",
        "PTRACTOR": "Contribution tractor policies",
        "PWERKT": "Contribution agricultural machines policies ",
        "PBROM": "Contribution moped policies",
        "PLEVEN": "Contribution life insurances",
        "PPERSONG": "Contribution private accident insurance policies",
        "PGEZONG": "Contribution family accidents insurance policies",
        "PWAOREG": "Contribution disability insurance policies",
        "PBRAND": "Contribution fire policies",
        "PZEILPL": "Contribution surfboard policies",
        "PPLEZIER": "Contribution boat policies",
        "PFIETS": "Contribution bicycle policies",
        "PINBOED": "Contribution property insurance policies",
        "PBYSTAND": "Contribution social security insurance policies",
        "AWAPART": "Number of private third party insurance 1 - 12",
        "AWABEDR": "Number of third party insurance (firms) ...",
        "AWALAND": "Number of third party insurane (agriculture)",
        "APERSAUT": "Number of car policies",
        "ABESAUT": "Number of delivery van policies",
        "AMOTSCO": "Number of motorcycle/scooter policies",
        "AVRAAUT": "Number of lorry policies",
        "AAANHANG": "Number of trailer policies",
        "ATRACTOR": "Number of tractor policies",
        "AWERKT": "Number of agricultural machines policies",
        "ABROM": "Number of moped policies",
        "ALEVEN": "Number of life insurances",
        "APERSONG": "Number of private accident insurance policies",
        "AGEZONG": "Number of family accidents insurance policies",
        "AWAOREG": "Number of disability insurance policies",
        "ABRAND": "Number of fire policies",
        "AZEILPL": "Number of surfboard policies",
        "APLEZIER": "Number of boat policies",
        "AFIETS": "Number of bicycle policies",
        "AINBOED": "Number of property insurance policies",
        "ABYSTAND": "Number of social security insurance policies",
}

L0 = {
        1: "High Income, expensive child",
        2: "Very Important Provincials",
        3: "High status seniors",
        4: "Affluent senior apartments",
        5: "Mixed seniors",
        6: "Career and childcare",
        7: "Dinki's (double income no kids)",
        8: "Middle class families",
        9: "Modern, complete families",
        10: "Stable family",
        11: "Family starters",
        12: "Affluent young families",
        13: "Young all american family",
        14: "Junior cosmopolitan",
        15: "Senior cosmopolitans",
        16: "Students in apartments",
        17: "Fresh masters in the city",
        18: "Single youth",
        19: "Suburban youth",
        20: "Etnically diverse",
        21: "Young urban have-nots",
        22: "Mixed apartment dwellers",
        23: "Young and rising",
        24: "Young, low educated ",
        25: "Young seniors in the city",
        26: "Own home elderly",
        27: "Seniors in apartments",
        28: "Residential elderly",
        29: "Porchless seniors: no front yard",
        30: "Religious elderly singles",
        31: "Low income catholics",
        32: "Mixed seniors",
        33: "Lower class large families",
        34: "Large family, employed child",
        35: "Village families",
        36: "Couples with teens 'Married with children'",
        37: "Mixed small town dwellers",
        38: "Traditional families",
        39: "Large religous families",
        40: "Large family farms",
        41: "Mixed rurals"
}

L1 = {
        1: "20-30 years",
        2: "30-40 years",
        3: "40-50 years",
        4: "50-60 years",
        5: "60-70 years",
        6: "70-80 years"
}

L2 = {
        1: "Successful hedonists",
        2: "Driven Growers",
        3: "Average Family",
        4: "Career Loners",
        5: "Living well",
        6: "Cruising Seniors",
        7: "Retired and Religeous",
        8: "Family with grown ups",
        9: "Conservative families",
        10: "Farmers"
}

L3 = {
        0: "0%",
        1: "1 - 10%",
        2: "11 - 23%",
        3: "24 - 36%",
        4: "37 - 49%",
        5: "50 - 62%",
        6: "63 - 75%",
        7: "76 - 88%",
        8: "89 - 99%",
        9: "100%"
}


def print_breakdown(df, key):
    x2y = df.groupby(key).mean()
    for key, val in x2y["CARAVAN"].items():
        print("{0:<25}{1:.1f}%".format(key, val*100))


def train_test_svm(df):
    X = df.loc[:, df.columns != "CARAVAN"].to_numpy()
    y = df["CARAVAN"].to_numpy()
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    model = SVC(class_weight="balanced")
    model.fit(X_train, y_train)

    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)

    #print("train_score: {0:.3f}".format(train_score))
    #print("test_score: {0:.3f}".format(test_score))

    print("Train score:")
    get_confusion_matrix(model, X_train, y_train)
    print()
    print("Test score:")
    get_confusion_matrix(model, X_test,  y_test)


def train_test_decision_tree(df):
    X = df.loc[:, df.columns != "CARAVAN"].to_numpy()
    #X = df.loc[:, ["MOSHOOFD", "MOSTYPE", "MGEMLEEF"]]
    y = df["CARAVAN"].to_numpy()
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    model = DecisionTreeClassifier(class_weight={0: 1, 1: 1 / np.mean(y_train)}, max_depth=3)
    model.fit(X_train, y_train)

    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)

    #print("train_score: {0:.3f}".format(train_score))
    #print("test_score: {0:.3f}".format(test_score))

    print("Train score:")
    get_confusion_matrix(model, X_train, y_train, y_train.mean())
    print()
    print("Test score:")
    get_confusion_matrix(model, X_test,  y_test, y_train.mean())


def get_confusion_matrix(model, X, y, base_p=0.5):
    log2base_p = -np.log2(base_p)
    log2comp_p = -np.log2(1 - base_p)


    yh = model.predict(X)

    prior_h = -relative_information_gain({0: y.mean()}, {0: 1}, log2base_p, log2comp_p)
    y_neg = [yhi for yhi, yi in zip(yh, y) if not yi]
    y_pos = [yhi for yhi, yi in zip(yh, y) if yi]
    posterior_h = -relative_information_gain({0: np.mean(y_neg), 1: np.mean(y_pos)},
                                             {0: len(y_neg) / len(X_test), 1: len(y_pos) / len(X_test)},
                                             log2base_p, log2comp_p)
    print("Prior:     {0:.3f}\nPosterior: {1:.3f}".format(prior_h, posterior_h))


    tp = np.dot(  y,   yh)
    fp = np.dot(1-y,   yh)
    fn = np.dot(  y, 1-yh)
    tn = np.dot(1-y, 1-yh)

    print("{0} {1}\n{2} {3}".format(tp, fp, fn, tn))


def relative_information_gain(a2p, a2n, log2base_p, log2comp_p):
    """
    a2p: average of y for each value of a
    a2n: relative frequency in the data for each value of a
    """

    #print(a2p)
    #print(a2n)

    def H(p):
        if p == 0 or p == 1:
            return 0
        return p * np.log2(p * log2base_p) + (1-p) * np.log2((1-p) * log2comp_p)

    return sum([a2n[a] * H(a2p[a]) for a in a2n if a in a2p])


def clump_small_categories(a2p, a2n, threshold):
    if "other" in a2p:
        raise AttributeError("'other' is a protected category label")

    small_cats = {a for a, n in a2n.items() if n <= threshold}
    n_other = sum(a2n[a] for a in small_cats)
    if not n_other:
        return a2p, a2n, list(a2p.keys())
    p_other = sum(a2p[a]*a2n[a] for a in small_cats) / n_other
    for cat in small_cats:
        a2p.pop(cat)
        a2n.pop(cat)
    nonsmall_cats = list(a2p.keys())
    a2p["other"] = p_other
    a2n["other"] = n_other
    return a2p, a2n, nonsmall_cats


def debug(*s):
    if 0:
        print(*s)

def build_DTC(T, root, df, y_key, base_p, depth):
    debug("\t" * (max_depth - depth) + root)
    debug("\t" * (max_depth - depth) + str(len(df)))
    if not len(df): 
        T.nodes[root]["feature"] = ""
        T.nodes[root]["class"] = 1 # no examples - guess positive
        return 

    if depth == 0:
        debug("\t" * (max_depth - depth) + "Exiting because of depth")
        T.nodes[root]["feature"] = ""
        T.nodes[root]["class"] = (df[y_key].sum() + 1) / (len(df) + 2)# > base_p
        return

    if df[y_key].mean() in [0, 1]:
        debug("\t" * (max_depth - depth) + "Exiting because of mean")
        T.nodes[root]["feature"] = ""
        # laplace probability of unseen
        T.nodes[root]["class"] = (df[y_key].sum() + 1) / (len(df) + 2) # > base_p
        return

    log2base_p = -np.log2(base_p)
    log2comp_p = -np.log2(1 - base_p)

    key2h = {}
    key2nonsmall = {}
    key2split_sign = {}

    for key in L:
        if key in categorical:
            a2p = df[[key, y_key]].groupby(key).mean()
            a2p = dict(a2p[y_key].items())
            a2n = df[[key, y_key]].groupby(key).count() # / len(df)
            a2n = dict(a2n[y_key].items())
            #if key == "MOSTYPE":
            #    print(a2n)

            a2p, a2n, nonsmall_cats = clump_small_categories(a2p, a2n, 5)
            a2n = {a: n / len(df) for a, n in a2n.items()}
            #if key == "MOSTYPE":
            #    print(nonsmall_cats)
            #    exit(0)
            key2nonsmall[key] = nonsmall_cats
        else: # numerical
            neg = df.loc[df[y_key] == 0][key] 
            pos = df.loc[df[y_key] == 1][key]
            neg_mean = neg.mean()
            pos_mean = pos.mean()
            split = (neg_mean + pos_mean) / 2
            sign = ((pos_mean >= neg_mean) - 0.5) * 2
            a2p = {}
            left_split = df[[key, y_key]].loc[df[key] * sign < split * sign]
            right_split = df[[key, y_key]].loc[df[key] * sign >= split * sign]
            a2p[0] = left_split[y_key].mean()
            a2p[1] = right_split[y_key].mean()
            #print(a2p)
            '''
            if key == "PBESAUT":
                print("split:", split)
                print("sign:", sign)
                print("a2p:", a2p)
                print("len neg:", len(neg))
                plt.hist([neg, pos])
                plt.show()
                #exit(0)
            '''
            a2n = {}
            a2n[0] = len(left_split) / len(df)
            a2n[1] = len(right_split) / len(df)
            key2nonsmall[key] = []
            key2split_sign[key] = (split, sign)

        key2h[key] = relative_information_gain(a2p, a2n, log2base_p, log2comp_p)

    #for key, h in sorted(key2h.items(), key=lambda x: -x[1]):
    #    print("\t{0:<50}{1:.5f}".format(L[key], h))
    #exit(0)

    key, h = max(key2h.items(), key=lambda x: x[1])

    T.nodes[root]["feature"] = key
    debug("\t" * (max_depth - depth) + L[key])
    nonsmall_cats = key2nonsmall[key]

    if key in categorical:
        for a, sub_df in df.groupby(key):
            if a not in nonsmall_cats:
                continue
            #print(a)
            #print(sub_df[key])
            #print()
            root_a = root + "_" + str(a)
            T.add_edge(root, root_a)
            build_DTC(T, root_a, sub_df, y_key, base_p, depth-1) # depth-first

        root_a = root + "_other"
        T.add_edge(root, root_a)
        other_x = df.loc[~df[key].isin(nonsmall_cats)]
        build_DTC(T, root_a, other_x, y_key, base_p, depth-1)
    else:
        split, sign = key2split_sign[key]
        T.nodes[root]["split"] = split
        T.nodes[root]["sign"]  = sign
        #print("split, sign:", split, sign)
        neg_df = df.loc[df[key] * sign < split * sign]
        pos_df = df.loc[df[key] * sign >= split * sign]

        root_a = root + "_0"
        T.add_edge(root, root_a)
        build_DTC(T, root_a, neg_df, y_key, base_p, depth-1)

        root_a = root + "_1"
        T.add_edge(root, root_a)
        build_DTC(T, root_a, pos_df, y_key, base_p, depth-1)


def classify(T, root, x):
    feature = T.nodes[root]["feature"]

    if not feature:
        return T.nodes[root]["class"]

    if feature in categorical:
        a = "_" + str(x[feature])
    
        if root+a in T[root]:
            root_a = root + a
        else:
            root_a = root + "_other"
    else:
        split = T.nodes[root]["split"]
        sign  = T.nodes[root]["sign"]
        a = int(x[feature] * sign >= split * sign)
        root_a = root + "_" + str(a)
    
    return classify(T, root_a, x)


def train_dtc(df):
    global max_depth
    max_depth = 20

    N_train = 4000
    X_train = df.loc[:N_train]

    root = "root"
    T = nx.DiGraph()
    T.add_node(root)
    y_key = "CARAVAN"
    base_p = X_train[y_key].mean() # balanced
    #base_p = 1 # unbalanced
    build_DTC(T, root, X_train, y_key, base_p, max_depth)

    log2base_p = -np.log2(base_p)
    log2comp_p = -np.log2(1 - base_p)

    #X_test = X_train 
    X_test = df.loc[N_train:]

    #print(T.nodes())
    for _, x in X_test.iterrows():
        yh = classify(T, root, x)

    yh = np.array([classify(T, root, x) for _, x in X_test.iterrows()])
    y = X_test[y_key]
    prior_h = -relative_information_gain({0: y.mean()}, {0: 1}, log2base_p, log2comp_p)
    y_neg = [yhi for yhi, yi in zip(yh, y) if not yi]
    y_pos = [yhi for yhi, yi in zip(yh, y) if yi]
    posterior_h = -relative_information_gain({0: np.mean(y_neg), 1: np.mean(y_pos)},
                                             {0: len(y_neg) / len(X_test), 1: len(y_pos) / len(X_test)},
                                             log2base_p, log2comp_p)
    print("Prior:     {0:.3f}\nPosterior: {1:.3f}".format(prior_h, posterior_h))

    yh = np.array([yhi > base_p for yhi in yh])

    tp = np.dot(  y,   yh)
    fp = np.dot(1-y,   yh)
    fn = np.dot(  y, 1-yh)
    tn = np.dot(1-y, 1-yh)

    print("{0} {1}\n{2} {3}".format(tp, fp, fn, tn))


    plt.hist([y_neg, y_pos], density=True, bins=50)
    plt.axvline(x=base_p, color="k")
    plt.show()

def main():
    t0 = time.time()
    #a2n = {0: 3/8, 1: 3/8, 2: 2/8}
    #a2p = {0: 2/3, 1: 1/3, 2: 1/2}
    #print(relative_information_gain(a2p, a2n))

    df = pd.read_csv("/home/jdw/garageofcode/data/kaggle/insurance/tic_2000_train_data.csv", delimiter=",")
    #y = df["CARAVAN"]
    # main_type = df["MOSHOOFD"]
    # subtype MOSTYPE
    # age MGEMLEEF
    # roman catholic MGODRK
    #print_breakdown(df, "MRELGE")
    #plt.hist(df["MINK3045"])
    #plt.show()

    #plt.scatter(df["MINK3045"], df["MINK7512"])
    #plt.hist2d(df["MINKM30"], df["MINK3045"])
    #plt.hist(df["MKOOPKLA"])
    #plt.show()
    #for key in L:
    #    plt.hist(df[key])
    #    plt.title(L[key])
    #    plt.show()
    #print(df["CARAVAN"].mean())
    train_test_svm(df)
    #train_test_decision_tree(df)

    #train_dtc(df)


    '''
    key2h = {}

    for key in L:
        a2p = df.groupby(key).mean()
        a2p = dict(a2p["CARAVAN"].items())
        a2n = df.groupby(key).count() / len(df)
        a2n = dict(a2n["CARAVAN"].items())
        key2h[key] = relative_information_gain(a2p, a2n)

    print(key2h)

    print("Prior entropy: {0:.5f}".format(relative_information_gain({0: df["CARAVAN"].mean()}, {0: 1})))


    for key, h in sorted(key2h.items(), key=lambda x: -x[1]):
        print("{0:<50}{1:.5f}".format(L[key], h))
    '''
    t1 = time.time()
    print("Total time: {0:.2f}".format(t1 - t0))




if __name__ == '__main__':
    main()