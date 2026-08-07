import matplotlib.pyplot as plt

import torch

from .base import TestFunction


class Sphere(TestFunction):

    name = "Sphere"

    minimize = True

    bounds = torch.Tensor(
        [[-5.12, -5.12], 
         [5.12, 5.12]]
    )

    optimum_input = torch.Tensor([[0., 0.]])

    info = "unimodal, " + \
           "continous, " + \
           "convex, " + \
           "smooth, " + \
           "symetric, " + \
           "straightforward"
    
    def evaluate(self, x1, x2):

        y = (
            x1**2 + x2**2
        )

        y = y.unsqueeze(0) if y.ndim == 0 else y

        return y.unsqueeze(-1)


if __name__ == "__main__":
    func = Sphere()
    fig, axs = func.plot(func.bounds)
    plt.show()