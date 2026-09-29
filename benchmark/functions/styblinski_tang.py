import matplotlib.pyplot as plt

import torch

from .base import TestFunction


class StyblinskiTang(TestFunction):

    name = "StyblinskiTang"

    minimize = True

    bounds = torch.Tensor(
        [[-5., -5.], 
         [5., 5.]]
    )

    optimum_input = torch.Tensor([[-2.903534, -2.903534]])

    info = "non-convex, " + \
           "multi-modal, " + \
           "deceptive shape"

    def evaluate(self, x1, x2):

        y = 0.5 * (
            x1**4 - 16 * x1**2 + 5 * x1 
            + x2**4 - 16 * x2**2 + 5 * x2
        )

        y = y.unsqueeze(0) if y.ndim == 0 else y

        return y.unsqueeze(-1)


if __name__ == "__main__":
    func = StyblinskiTang()
    fig, axs = func.plot(func.bounds)
    plt.show()