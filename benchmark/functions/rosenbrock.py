import matplotlib.pyplot as plt

import torch

from .base import TestFunction


class Rosenbrock(TestFunction):

    name = "Rosenbrock"

    minimize = True

    bounds = torch.Tensor(
        [[-2., -1.], 
         [2., 3.]]
    )

    global_min = [1., 1.] # [a, a**2]

    info = "non-convex, " + \
           "The global minimum is inside a long," + \
            "narrow, parabolic-shaped flat valley"

    def evaluate(self, x1, x2):

        a = 1.
        b = 100.
        
        y = (
            ( a - x1 )**2
            + b * ( x2 - x1**2 )**2
        )

        y = y.unsqueeze(0) if y.ndim == 0 else y

        return y.unsqueeze(-1)


if __name__ == "__main__":
    func = Rosenbrock()
    fig, axs = func.plot(func.bounds)
    plt.show()