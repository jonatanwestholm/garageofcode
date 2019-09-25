import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

class MLP(nn.Module):
    def __init__(self, sizes, activation=nn.ReLU(), out_activation=None):
        super(MLP, self).__init__()
        self.module_list = nn.ModuleList()

        for in_size, out_size in zip(sizes[:-1], sizes[1:]):
            self.module_list.append(nn.Linear(in_size, out_size))

        self.h = activation
        if out_activation is None:
            self.y = lambda x: x
        else:
            self.y = out_activation

    def forward(self, x):
        for mod in self.module_list[:-1]:
            #print(x)
            x = mod(x)
            x = self.h(x)
        x = self.module_list[-1](x)
        y = self.y(x)
        #y = y.view(list(y.shape) + [1])
        return y