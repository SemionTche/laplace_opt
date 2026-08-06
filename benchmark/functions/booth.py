import matplotlib.pyplot as plt

import torch

from .base import TestFunction


class Booth(TestFunction):

    name = "Booth"

    minimize = True

    bounds = torch.Tensor(
        [[-10., -10.], 
         [10., 10.]]
    )

    optimum_input = [1., 3.]

    info = "continuos, " + \
           "convex, " + \
           "unimodal, " + \
           "straightforward"
    
    def evaluate(self, x1, x2):

        y = (
            ( x1 + 2 * x2 - 7 )**2 
            + ( 2 * x1 + x2 - 5 )**2
        )

        y = y.unsqueeze(0) if y.ndim == 0 else y

        return y.unsqueeze(-1)


if __name__ == "__main__":
    func = Booth()
    fig, axs = func.plot(func.bounds)
    plt.show()