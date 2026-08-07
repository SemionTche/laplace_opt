import matplotlib.pyplot as plt

import torch

from .base import TestFunction


class Ackley(TestFunction):

    name = "Ackley"

    minimize = True

    bounds: torch.Tensor = torch.Tensor(
        [[-5., -5.], 
         [5., 5.]]
    )

    optimum_input = torch.Tensor([[0., 0.]])

    info = "non-convex, " + \
           "fine-textured broadly unimodal space, i.e. " + \
           "a wide, nearly flat outer region containing a deep central hole with many local minima"

    def evaluate(self, x1, x2):

        a = 20.
        b = 0.2
        c = 2 * torch.pi

        y = (
            -a * torch.exp( -b * torch.sqrt( (x1**2 + x2**2) / 2 ) )
            - torch.exp( ( torch.cos(c * x1) + torch.cos(c * x2) ) / 2 )
            + a
            + torch.exp(torch.tensor(1.))
        )

        y = y.unsqueeze(0) if y.ndim == 0 else y

        return y.unsqueeze(-1)


if __name__ == "__main__":
    func = Ackley()
    fig, axs = func.plot(func.bounds)
    plt.show()