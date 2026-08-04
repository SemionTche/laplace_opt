
import matplotlib.pyplot as plt

import torch

from .base import TestFunction


class Beale(TestFunction):

    name = "Beale"

    minimize = True

    bounds = torch.Tensor(
        [[-4.5, -4.5], 
         [4.5, 4.5]]
    )

    global_min = [3., 0.5]

    info = "multimodal, " + \
           "sharp peaks at the corners, " + \
           "flat area near the optimum"

    def evaluate(self, x1, x2) -> torch.Tensor:

        y = (
            ( 1.5 - x1 + x1 * x2 )**2
            + ( 2.25 - x1 + x1 * x2**2 )**2
            + ( 2.625 - x1 + x1 * x2**3 )**2
        )

        y = y.unsqueeze(0) if y.ndim == 0 else y

        return y.unsqueeze(-1)


if __name__ == "__main__":
    func = Beale()
    fig, axs = func.plot(func.bounds)
    plt.show()