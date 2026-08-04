import matplotlib.pyplot as plt

import torch

from .base import TestFunction


class GoldsteinPrice(TestFunction):

    name = "GoldsteinPrice"

    minimize = True

    bounds = torch.Tensor(
        [[-2., -2.], 
         [2., 2.]]
    )

    global_min = [0., 1.]

    info = "on global min, " + \
           "several local min, " + \
           "steep walls"

    def evaluate(self, x1, x2):

        a = 1 + (x1+x2+1)**2 * (
            19 - 14*x1 + 3*x1**2 - 14*x2 + 6*x1*x2 + 3*x2**2
        )

        b = 30 + (2*x1-3*x2)**2 * (
            18 - 32*x1 + 12*x1**2 + 48*x2
            - 36*x1*x2 + 27*x2**2
        )

        y = -(a*b)

        y = y.unsqueeze(0) if y.ndim == 0 else y

        return y.unsqueeze(-1)


if __name__ == "__main__":
    func = GoldsteinPrice()
    fig, axs = func.plot(func.bounds)
    plt.show()