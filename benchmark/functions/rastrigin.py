import matplotlib.pyplot as plt

import torch

from .base import TestFunction


class Rastrigin(TestFunction):

    name = "Rastrigin"

    minimize = True

    bounds = torch.Tensor(
        [[-5.12, -5.12], 
         [5.12, 5.12]]
    )

    optimum_input = [0., 0.]

    info = "non-convex, " + \
           "multi-modal, " + \
           "A smooth parabolic global " + \
            "trend guides search paths " + \
            "toward the general area of the origin, " + \
            "but local cosine modulations obscure the exact global minimum"

    def evaluate(self, x1, x2):

        A = 10.

        y = (
            A * self.n_inputs 
            + x1**2 - A * torch.cos(2 * torch.pi * x1)
            + x2**2  - A * torch.cos(2 * torch.pi * x2)
        )

        y = y.unsqueeze(0) if y.ndim == 0 else y

        return y.unsqueeze(-1)


if __name__ == "__main__":
    func = Rastrigin()
    fig, axs = func.plot(func.bounds)
    plt.show()