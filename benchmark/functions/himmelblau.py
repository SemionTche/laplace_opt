import matplotlib.pyplot as plt

import torch

from .base import TestFunction


class Himmelblau(TestFunction):

    name = "Himmelblau"

    minimize = True

    bounds = torch.Tensor(
        [[-6., -6.], 
         [6., 6.]]
    )

    optimum_input = torch.Tensor(
        [[3., 2.],
         [-2.805118, 3.131312],
         [-3.779310, -3.283186],
         [3.584428, -1.848126]]
    )

    local_max = [-0.270845, -0.923039]

    info = "multi-modal, " + \
           "non-convex, " + \
           "4 global minima, " + \
           "1 local maximum"

    def evaluate(self, x1, x2):

        y = (
            ( x1**2 + x2 - 11 )**2 
            + ( x1 + x2**2 - 7 )**2
        )

        y = y.unsqueeze(0) if y.ndim == 0 else y

        return y.unsqueeze(-1)


if __name__ == "__main__":
    func = Himmelblau()
    fig, axs = func.plot(func.bounds)
    plt.show()