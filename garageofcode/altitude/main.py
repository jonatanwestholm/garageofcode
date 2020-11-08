import os
import re
from mpl_toolkits.mplot3d import Axes3D

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def sparsify(fn, out_fn, sparse_factor):
    with open(out_fn, "w") as fo:
        with open(fn, "r") as f:
            for idx, line in enumerate(f):
                if idx % sparse_factor == 0:
                    fo.write(line)

def filter_box(fn, out_fn, box_x0, box_x1, box_y0, box_y1):
    total_lines = 0
    with open(out_fn, "w") as fo:
        with open(fn, "r") as f:
            for line in f:
                line = re.sub(",", ".", line)
                x, y, z = line.split(" ")
                x, y, z = float(x), float(y), float(z)
                if box_x0 <= x <= box_x1 and box_y0 <= y <= box_y1:
                    fo.write(line)
                    total_lines += 1
    print(fn, ":", total_lines)

def join_texts(d):
    filenames = [fn[:-1] for fn in os.popen("ls {}".format(d)) if ".xyz" in fn]
    filenames = list(sorted(filenames))

    s = "\n".join([open(os.path.join(d, fn), "r").read()[:-1] for fn in filenames])

    out_name = os.path.join(d, "out")
    s = re.sub(",", ".", s)
    f = open(out_name, "w")
    f.write(s)


def bin_map(fn, save_fn):    
    eps = 1e-6
    min_x, max_x = 600000.0,  771701.6
    min_y, max_y = 6400000.0, 6700000.0

    #min_x, max_x = np.min(X), np.max(X)
    #min_y, max_y = np.min(Y), np.max(Y)
    res_x = 1000
    res_y = 1000
    #diff_x = (max_x - min_x) / res
    #diff_y = (max_y - min_y) / res

    A = np.zeros([res_y, res_x])
    N = np.ones([res_y, res_x])*eps

    box_x0, box_x1 = 650000,  700000
    box_y0, box_y1 = 6550000, 6600000
    diff_x = (box_x1 - box_x0) / res_x
    diff_y = (box_y1 - box_y0) / res_y

    for line in open(fn, "r"):
        x, y, z = line.split(" ")
        x, y, z = float(x), float(y), float(z)
        if box_x0 <= x <= box_x1 and box_y0 <= y <= box_y1:
            #xi = int((x - min_x) / diff_x - eps)
            #yi = int((y - min_y) / diff_y - eps)
            xi = int((x - box_x0) / diff_x - eps)
            yi = int((y - box_y0) / diff_y - eps)
            #A[res - 1 - yi, xi] += z
            #N[res - 1 - yi, xi] += 1
            A[res_y - 1 - yi, xi] += z
            N[res_y - 1 - yi, xi] += 1

    b = 2**16 - 1
    alt = np.divide(A, N)
    max_z = np.max(alt)
    alt = (alt - eps) / max_z * b
    alt = alt.astype(np.uint16)

    #print(N[50:70, 50:70])

    #fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')
    #ax.scatter(x, y, z)
    #plt.imshow(alt[100:500, 100:600])
    #plt.show()

    img = Image.fromarray(alt[100:500, 100:600])
    img.save(save_fn, compress_level=0)


def scatter3d(fn):
    def line2xyz(line):
        x, y, z = line.split(" ")
        return float(x), float(y), float(z)

    x, y, _ = zip(*[line2xyz(line) for line in open(fn, "r")])
    plt.scatter(x, y)
    plt.show()


def overlay_altitude(map_fn, alt_fn):
    map_img = np.array(Image.open(map_fn))
    alt_img = np.array(Image.open(alt_fn))

    map_max = np.max(map_img)
    map_img = map_img / map_max
    alt_max = np.max(alt_img)
    alt_img = alt_img / alt_max


    #print(map_img.shape)
    #print(alt_img.shape)

    map_img[:400, :500, 0] += alt_img

    plt.imshow(map_img)
    plt.show()


if __name__ == '__main__':
    in_dir = "/home/jdw/garageofcode/data/altitude/stockholm/"
    out_dir = "/home/jdw/garageofcode/results/altitude/stockholm/"
    if 0:
        sparse_factor = 5
        filenames = [fn[:-1] for fn in os.popen("ls {}".format(in_dir)) if ".xyz" in fn]
        for fn in filenames:
            sparsify(in_dir + fn, out_dir + fn, sparse_factor)
        join_texts(out_dir)
    if 0:
        box_x0, box_x1 = 650000,  700000
        box_y0, box_y1 = 6550000, 6650000
        for fn in ["hdb_65_6.xyz", "hdb_66_6.xyz"]:
            filter_box(in_dir + fn, out_dir + fn, box_x0, box_x1, box_y0, box_y1)
        join_texts(out_dir)

    #bin_map(out_dir + "out", out_dir + "overlay.png")    
    #scatter3d(out_dir + "out")
    overlay_altitude(out_dir + "sthlm.png", out_dir + "overlay.png")




