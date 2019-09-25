import numpy as np
import matplotlib.pyplot as plt

def koch(line):
    p0, p1 = line
    mid0 = (1 - 0.25) * p0 + 0.25 * p1
    mid2 = (1 - 0.75) * p0 + 0.75 * p1

    a, b = p1 - p0
    normal = np.array([-b, a])
    mid1 = 0.5 * p0 + 0.5 * p1
    mid1 = mid1 + np.sqrt(3) / 2 / 3 * normal

    return (p0, mid0), (mid0, mid1), (mid1, mid2), (mid2, p1)

def koch_expand(lines):
    return [l for line in lines for l in koch(line)]

def noise():
    return np.random.normal([2]) * 0.005

def triforce(tri):
    p0, p1, p2 = tri

    l0 = np.random.random()*0.2 + 0.4
    l1 = np.random.random()*0.2 + 0.4
    l2 = np.random.random()*0.2 + 0.4

    mid0 = (1 - l0) * p1 + l0 * p2 + noise()
    mid1 = (1 - l1) * p2 + l1 * p0 + noise()
    mid2 = (1 - l2) * p0 + l2 * p1 + noise()

    return [(p0, mid1, mid2), 
           (p1, mid2, mid0), 
           (p2, mid0, mid1), 
           (mid0, mid1, mid2)]

def triforce_expand(tris):
    return [t for tri in tris for t in triforce(tri)]

def koch_main():
    p0 = np.array([0, 0])
    p1 = np.array([1, 0])

    lines = [(p0, p1)]

    for _ in range(5):
        lines = koch_expand(lines)

    for line in lines:
        (x0, y0), (x1, y1) = line
        plt.plot([x0, x1], [y0, y1], 'b')
        #plt.draw()
        #plt.pause(0.01)

    plt.show()

def tri_main():
    p0 = np.array([0, 0])
    p1 = np.array([0.5, np.sqrt(3) / 2])
    p2 = np.array([1, 0])

    tris = [(p0, p1, p2)]

    for _ in range(4):
        tris = triforce_expand(tris)


    color = 'b'

    for tri in tris:
        (x0, y0), (x1, y1), (x2, y2) = tri
        plt.plot([x0, x1], [y0, y1], color=color)
        plt.plot([x0, x2], [y0, y2], color=color)
        plt.plot([x2, x1], [y2, y1], color=color)

    plt.show()

if __name__ == '__main__':
    tri_main()