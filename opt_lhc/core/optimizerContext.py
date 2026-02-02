# libraries
from dataclasses import dataclass

import torch
from botorch.utils.transforms import normalize

from laplace_log import log

@dataclass
class Observation:
    x: torch.Tensor    # shape [d]
    y: torch.Tensor    # shape [n_obj]


class OptimizationContext:
    '''
    '''
    def __init__(self, bounds, objectives):
        '''
        '''
        self.bounds = bounds
        self.objectives = objectives
        self.n_obj = len(self.objectives)

        self._observations: list[Observation] = []
        log.debug("Context created.")

    
    def add_observation(self, x: torch.Tensor, y: torch.Tensor) -> None:
        """
        x: shape [d]
        y: shape [n_obj]
        """
        self._observations.append(Observation(x=x, y=y))


    def add_observations(self, observations: list[Observation]) -> None:
        self._observations.extend(observations)


    def X_by_objective(self) -> list[torch.Tensor]:
        Xs = [[] for _ in range(self.n_obj)]

        for obs in self._observations:
            for i in range(self.n_obj):
                if not torch.isnan(obs.y[i]):
                    Xs[i].append(obs.x)

        return [
            torch.stack(x) if x else torch.empty(0, self.bounds.shape[1], dtype=torch.double)
            for x in Xs
        ]
    

    def Y_by_objective(self) -> list[torch.Tensor]:
        Ys = [[] for _ in range(self.n_obj)]

        for obs in self._observations:
            for i in range(self.n_obj):
                if not torch.isnan(obs.y[i]):
                    Ys[i].append(obs.y[i:i+1])

        return [
            torch.stack(y) if y else torch.empty(0, 1, dtype=torch.double)
            for y in Ys
        ]


    def get_X_baseline(self) -> torch.Tensor:
        if not self._observations:
            raise RuntimeError("No baseline points available.")

        X = torch.stack([obs.x for obs in self._observations])
        return torch.unique(X, dim=0)


    def compute_ref_point(self) -> torch.Tensor:
        ref = []

        Y = torch.stack([obs.y for obs in self._observations])

        for i, obj in enumerate(self.objectives.values()):
            yi = Y[:, i]

            if obj.minimize:
                ref.append(yi.max() + 0.1 * yi.abs().max())
            else:
                ref.append(yi.min() - 0.1 * yi.abs().max())

        return torch.tensor(ref, dtype=torch.double)


    
    # def get_X_baseline(self) -> torch.Tensor:
    #     """
    #     Return the union of all evaluated design points,
    #     suitable for NEHVI / LogNEHVI.
    #     """
    #     Xs = []

    #     for X in self.train_X_list:
    #         if isinstance(X, torch.Tensor) and X.numel() > 0:
    #             Xs.append(X)

    #     if len(Xs) == 0:
    #         raise RuntimeError("No baseline points available.")

    #     # concatenate and drop duplicates
    #     X_all = torch.cat(Xs, dim=0)
    #     X_unique = torch.unique(X_all, dim=0)

    #     return X_unique
    
    def get_X_baseline_normalized(self) -> torch.Tensor:
        return normalize(self.get_X_baseline(), self.bounds)
    

    # def compute_ref_point(self) -> torch.Tensor:
    #     ref = []
    #     for i, obj in enumerate(self.objectives.values()):
    #         y = self.train_Y_list[i].squeeze(-1)

    #         if obj.minimize:
    #             ref.append(y.max() + 0.1 * y.abs().max())
    #         else:
    #             ref.append(y.min() - 0.1 * y.abs().max())

    #     return torch.tensor(ref, dtype=torch.double)
