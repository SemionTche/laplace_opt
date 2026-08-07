import matplotlib.pyplot as plt

import torch

from .base import TestFunction


class BraninHoo(TestFunction):

    name = "Branin"

    minimize = True

    bounds = torch.Tensor(
        [[-5., 0.], 
         [10., 15.]]
    )

    optimum_input = torch.Tensor(
        [[-torch.pi, 12.275], 
         [torch.pi, 2.275], 
         [9.42478, 2.475]]
    )

    info = "3 global minima"

    def evaluate(self, x1, x2):

        a = 1.
        b = 5.1 / (4 * torch.pi**2)
        c = 5 / torch.pi
        r = 6.
        s = 10.
        t = 1 / (8 * torch.pi)

        y = (
            a * ( x2 - b * x1**2 + c * x1 - r )**2 
            + s * ( 1 - t ) * torch.cos(x1) 
            + s
        )

        y = y.unsqueeze(0) if y.ndim == 0 else y

        return y.unsqueeze(-1)


if __name__ == "__main__":
    func = BraninHoo()
    fig, axs = func.plot(func.bounds)
    plt.show()