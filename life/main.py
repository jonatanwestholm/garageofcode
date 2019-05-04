import numpy as np

alphabet = ["A", "B", "C", "vC"]
n_a = len(alphabet)

p2decay = {"A": 0.01, "B": 0.01, "C": 0.01, "C0": 0.1}
p2attach = {"A": 0.1, "B": 0.1, "C": 0.1}

class Head:
    def __init__(self, N):
        self.N = N
        self.tape = [alphabet[np.random.randint(n_a)] for _ in range(self.N)]
        self.head = 0
        self.mode = "reading"

    def push(self, protein):
        if mode == "mute":
            if protein == "vC":
                self.mode = "reading"
            return None
        elif mode == "reading":
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

class Environment:
    def __init__(self):
        self.t = 0
        self.p2num = {"A": 10, "B": 10, "C": 10, "C0": 1}

    def next(self):
        p2decay_total = {p: p2decay[p] * self.p2num[p] for p in self.p2num}
        time_to_next = [(np.random.exponential(intensity), (p, "decay")) 
                            for p, intensity in p2decay_total.items()]
        p2attach_total = {p: p2attach[p] * self.p2num[p] for p in p2attach}
        time_to_next.append([(np.random.exponential(intensity), (p, "attach")) 
                             for p, intensity in p2attach_total.items()])

        t, (p, action) = min(time_to_next)
        self.t += t

        if action == "attach":
            return p
        elif action == "decay":
            if p == "C0":
                return "vC"
            else:
                self.p2num[p] -= 1
                return None
        else:
            return None

def main():
    head = Head()
    env = Environment()

    for _ in range(100):
        protein = env.next()
        output = head.push(protein)
        env.push(output)

if __name__ == '__main__':
    main()