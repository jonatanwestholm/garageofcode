import numpy as np
import matplotlib.pyplot as plt

alphabet = ["A", "B", "C", "vC"]
n_a = len(alphabet)

p2num = {"A": 10, "B": 10, "C": 10, "C0": 1}
p2decay = {"A": 0.01, "B": 0.01, "C": 0.01, "C0": 0.1}
p2attach = {"A": 0.1, "B": 0.1, "C": 0.01}

class Head:
    def __init__(self, N):
        self.N = N
        self.tape = [alphabet[np.random.randint(n_a-1)] for _ in range(self.N)]
        self.head = 0
        self.mode = "reading"

    def push(self, protein):
        if protein is None:
            return None

        if self.mode == "mute":
            if protein == "vC":
                self.mode = "reading"
            return None
        elif self.mode == "reading":
            if protein == "A":
                self.head = (self.head + 1) % self.N
                return self.tape[self.head]
            elif protein == "B":
                self.head = (self.head - 1) % self.N
                return self.tape[self.head]
            elif protein == "C":
                self.mode = "mute"
                return None
            else:
                return None
        else:
            return None

    def draw(self, ax):
        ax.cla()

        margin = 4
        upper = 0.5
        lower = -0.5
        ax.plot([-(margin + 1), margin + 1], [upper, upper], 'k')
        ax.plot([-(margin + 1), margin + 1], [lower, lower], 'k')
        for x in range(-margin, margin+2):
            ax.plot([x-0.5, x-0.5], [lower, upper], 'k')
            if x <= margin:
                sym = self.tape[(self.head + x) % self.N]
                ax.text(x, 0, sym, color='r')

        if self.mode == "reading":
            col = 'g'
        else:
            col = 'r'
        ax.plot([-0.5, 0.5], [lower, lower], col, linewidth=3)
        ax.plot([0.5, 0.5], [lower, upper], col, linewidth=3)
        ax.plot([-0.5, 0.5], [upper, upper], col, linewidth=3)
        ax.plot([-0.5, -0.5], [lower, upper], col, linewidth=3)

        ax.set_ylim([lower-5, upper + 5])

        ax.axis("off")

class Environment:
    def __init__(self):
        self.t = 0
        self.p2num = p2num
        self.p2num_history = {p: [num] for p, num in self.p2num.items()}
        self.t_history = [self.t]

    def next(self):
        """
        Draw the next event from the environment
        """
        p2decay_total = {p: p2decay[p] * self.p2num[p] for p in self.p2num}
        time_to_next = [(np.random.exponential(1 / intensity), (p, "decay")) 
                            for p, intensity in p2decay_total.items() if intensity]
        p2attach_total = {p: p2attach[p] * self.p2num[p] for p in p2attach}
        time_to_next.extend([(np.random.exponential(1 / intensity), (p, "attach")) 
                             for p, intensity in p2attach_total.items() if intensity])

        t, (p, action) = min(time_to_next, key=lambda x: x[0])
        print("Action:", "{0:.3f}".format(t), p, action)
        self.t += t
        self.t_history.append(self.t)
        for prot in self.p2num:
            self.p2num_history[prot].append(self.p2num[prot])

        if action == "attach":
            return p
        elif action == "decay":
            if p == "C0":
                return "vC"
            else:
                self.p2num[p] = self.p2num[p] - 1
                self.p2num_history[p][-1] = self.p2num[p]
                return None
        else:
            return None

    def push(self, protein):
        """
        Add a single protein to the environment
        """
        if protein is None:
            return

        for p in self.p2num:
            self.p2num_history[p].append(self.p2num[p])
        self.p2num[protein] = self.p2num[protein] + 1
        self.p2num_history[protein][-1] = self.p2num[protein]
        self.t_history.append(self.t)

    def draw(self, ax):
        ax.cla()
        for p, nums in sorted(self.p2num_history.items()):
            ax.plot(self.t_history, nums)

        ax.legend(list(sorted(self.p2num.keys())))
        ax.set_xlabel("time")
        ax.set_ylabel("number of proteins")
        ax.set_title("Concentrations")

def main():
    head = Head(10)
    env = Environment()

    fig, (ax_env, ax_head) = plt.subplots(ncols=2)

    for _ in range(10000):
        protein = env.next()
        output = head.push(protein)
        env.push(output)
        env.draw(ax_env)
        head.draw(ax_head)
        plt.draw()
        plt.pause(0.01)

if __name__ == '__main__':
    main()