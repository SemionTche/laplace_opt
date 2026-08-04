from abc import ABC, abstractmethod
import matplotlib.pyplot as plt

import torch


class TestFunction(ABC):

    name = "Unnamed"

    minimize: bool = True

    bounds: torch.Tensor = torch.Tensor(
        [[-5., -5.], 
         [5., 5.]]
    )

    n_inputs = 2
    n_objectives = 1
    mode = "single"

    def __call__(self, *x):

        return self.evaluate(*x)


    @abstractmethod
    def evaluate(self, *x) -> torch.Tensor:

        pass


    def grid(self, bounds, n_points: int):

        # bounds shape: (2, d)
        axes = [
            torch.linspace(bounds[0, i], bounds[1, i], n_points)
            for i in range(bounds.shape[1])
        ]

        mesh = torch.meshgrid(*axes, indexing="xy")

        # Flatten grid for function evaluation
        points = torch.stack(
            [m.reshape(-1) for m in mesh],
            dim=-1
        )

        return mesh, points


    def plot(self, bounds=None, n_points=50):

        if bounds is None:
            bounds = self.bounds

        mesh, points = self.grid(bounds, n_points)

        # Coordinates
        X1 = mesh[0]
        X2 = mesh[1]

        # Evaluate function on flattened grid
        y = self.evaluate(points[:, 0], points[:, 1])

        # Reshape output back into grid
        y = y.reshape(n_points, n_points)

        fig, ax = plt.subplots(figsize=(6, 5))

        contour = ax.contourf(
            X1,
            X2,
            y,
            levels=50
        )

        fig.colorbar(contour, ax=ax)

        ax.set_xlabel("x1")
        ax.set_ylabel("x2")
        ax.set_title(self.name)

        return fig, ax