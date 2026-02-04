# libraries
from dataclasses import dataclass

import torch
from botorch.utils.transforms import normalize

from laplace_log import log

@dataclass
class Observation:
    '''
    Represents a single evaluation result of the optimizer.

    Attributes:
        x: (torch.Tensor)
            Input vector for the evaluation.
        y: (torch.Tensor)
            Corresponding objective values.
    '''
    x: torch.Tensor    # shape [d]
    y: torch.Tensor    # shape [n_obj]


class OptimizationContext:
    '''
    Stores training data, bounds, and objectives for optimization.

    Provides methods to access baseline points and compute reference points
    for acquisition functions.
    '''
    def __init__(self, bounds, objectives):
        '''
        Initialize the optimization context with problem definition.

        Args:
            bounds: (torch.Tensor) 
                Bounds for each input variable.

            objectives: (dict)
                Dictionary of objectives to optimize.
        '''
        self.bounds = bounds
        self.objectives = objectives
        self.n_obj = len(self.objectives)

        self._observations: list[Observation] = []
        log.debug("Context created.")

    @property
    def Y_physical(self):
        Y = torch.stack([obs.y for obs in self._observations])
        Y_physical = Y.clone()

        for i, obj in enumerate(self.objectives.values()):
            if obj.minimize:
                Y_physical[:, i] *= -1
        return Y_physical

    
    def add_observation(self, x: torch.Tensor, y: torch.Tensor) -> None:
        '''
        Add a single observation to the context.

        Args:
            x: (torch.Tensor)
                Input vector of shape [d].
            y: (torch.Tensor)
                Corresponding objective values of shape [n_obj].
                (take the opposite value in case of minimization)
        '''
        y_corrected = y.clone()
        for i, obj in enumerate(self.objectives.values()):
            if obj.minimize:
                y_corrected[i] = -y_corrected[i]
        
        self._observations.append(Observation(x=x, y=y_corrected))
        log.debug(f"Observation added: x={x.tolist()}, y={y_corrected.tolist()}")
        # self._observations.append(Observation(x=x, y=y))
        # log.debug(f"Observation added: x={x.tolist()}, y={y.tolist()}")


    def add_observations(self, observations: list[Observation]) -> None:
        '''
        Add multiple observations at once.

        Args:
            observations: (list[Observation])
                List of Observation instances.
        '''
        self._observations.extend(observations)
        log.debug(f"{len(observations)} observations added. Total now: {len(self._observations)}")


    def X_by_objective(self) -> list[torch.Tensor]:
        '''
        Get input tensors grouped by objective.

        Returns:
            list[torch.Tensor]: 
                List of tensors, one per objective, containing 
                the input vectors for valid observations.
        '''
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
        '''
        Get output tensors grouped by objective.

        Returns:
            list[torch.Tensor]: 
                List of tensors, one per objective, containing 
                the corresponding objective values.        
        '''
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
        '''
        Get all unique evaluated input points.

        Returns:
            torch.Tensor: 
                Concatenated and unique inputs across all observations.        
        '''
        if not self._observations:
            log.warning("No baseline points available.")

        X = torch.stack([obs.x for obs in self._observations])
        log.debug(f"Baseline points retrieved: {X.shape[0]} points")
        return torch.unique(X, dim=0)
    

    def get_X_baseline_normalized(self) -> torch.Tensor:
        '''
        Get normalized baseline inputs according to bounds.

        Returns:
            torch.Tensor: 
                Normalized unique input points.
        '''
        return normalize(self.get_X_baseline(), self.bounds)


    def compute_ref_point(self) -> torch.Tensor:
        '''
        Compute a reference point for multi-objective optimization.

        The reference correspond to the **optimized space**.

        Returns:
            torch.Tensor: 
                Reference point vector of shape [n_obj].
        '''
        # ref = []

        Y = torch.stack([obs.y for obs in self._observations])

        ref = Y.min(dim=0).values - 0.1 * Y.abs().max(dim=0).values

        return ref


    def compute_ref_point_physical(self):
        '''
        Compute a reference point for multi-objective optimization.

        The reference correspond to the **physical space**.

        Returns:
            torch.Tensor: 
                Reference point vector of shape [n_obj].
        '''
        ref = self.compute_ref_point()
        for i, obj in enumerate(self.objectives.values()):
            if obj.minimize:
                ref[i] *= -1
        return ref