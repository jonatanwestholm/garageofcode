import numpy as np
import matplotlib.pyplot as plt

def get_random(freqs):
    freq_vec = sum([[k]*num for k, num in freqs.items()], [])
    N = len(freq_vec)
    while True:
        idx = np.random.randint(0, N)
        yield freq_vec[idx]


def write_random_sequence(fn, freqs, n):
    with open(fn, "w") as f:
        reader = iter(get_random(freqs))
        for _ in range(n):
            f.write("{}".format(next(reader)))


def entropy(values):
    values = np.array(values) / np.sum(values)
    return sum(p * (-np.log2(p)) for p in values)


def encode(reader, predictor):
    a2width = predictor
    idx2a, idx2p = zip(*sorted(predictor.items()))
    idx2P = np.cumsum(idx2p)  # distribution function
    idx2lb = [0] + list(idx2P)[:-1]
    a2lb = dict(zip(idx2a, idx2lb))

    while True:
        width = 2**8
        lb = 0 # lower bound
        while width > 1:
            try:
                a = next(reader)
            except StopIteration:
                return
            lb += int(width*a2lb[a])
            width *= a2width[a]

        yield lb


def decode(reader, predictor):
    a2width = predictor
    idx2a, idx2p = zip(*sorted(predictor.items()))
    idx2P = np.cumsum(idx2p)  # distribution function
    idx2lb = list(idx2P) 
    a2lb = dict(zip(idx2a, idx2lb))
    N = len(a2width)

    while True:
        try:
            seq = get_seq(reader)
        except StopIteration:
            break

        width = 2**8
        lb = 0
        while True:
            idx = 0
            while seq >= lb + int(idx2lb[idx] * width):
                idx += 1
            lb += int(idx2lb[idx] * width)
            width *= idx2p[idx]
            width = int(width)
            if not width:
                break
            yield idx2a[idx]


def get_seq(reader):
    seq = []
    while True:
        a = next(reader)
        if a in "0123456789":
            seq.append(a)
        else:
            return int("".join(seq))


if __name__ == '__main__':
    freqs = {"0": 3, "1": 1}  # relative frequencies
    sum_freqs = sum(freqs.values())
    predictor = {k: v / sum_freqs for k, v in freqs.items()}
    #H = entropy([1, 1, 1, 1, 1, 1, 1, 1])
    #H = entropy(list(freqs.values()))
    #print("entropy of distribution: {0:.3f}".format(H))
    fn = "random_1000.txt"
    fn_compressed = fn.split(".")[0] + ".azip"
    fn_reconstructed = fn.split(".")[0] + "_rec.txt"
    #write_random_sequence(fn, freqs, 3)

    with open(fn, "r") as r:
        reader = iter(r.read())
        with open(fn_compressed, "w") as f:
            for seq in encode(reader, predictor):
                f.write("{}\n".format(seq))

    with open(fn_compressed, "r") as r:
        reader = iter(r.read())
        with open(fn_reconstructed, "w") as f:
            for a in decode(reader, predictor):
                f.write("{}".format(a))

    '''
    with open(fn, "r") as r:
        reader = iter(r.read())
        lbs = list(encode(reader, predictor))
    plt.hist(lbs)
    plt.title("Histogram of codes: uniform distribution")
    plt.xlabel("code (number)")
    plt.ylabel("frequency")
    plt.show()
    '''
