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
    def Y_opt_space(self):
        return torch.stack([obs.y for obs in self._observations])

    @property
    def Y_physical(self):
        Y = self.Y_opt_space
        Y_physical = self._to_physical(Y)
        return Y_physical
    
    def _to_physical(self, Y_opt: torch.Tensor) -> torch.Tensor:
        Y_phys = Y_opt.clone()
        for i, obj in enumerate(self.objectives.values()):
            if obj.minimize:
                Y_phys[:, i] *= -1
        return Y_phys

    @property
    def X_physical(self) -> torch.Tensor:
        X = torch.stack([obs.x for obs in self._observations])
        return X
    
    @property
    def X_normalized(self) -> torch.Tensor:
        return normalize(self.X_physical, self.bounds)
    

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


    def add_observations(self, observations: list[Observation]) -> None:
        '''
        Add multiple observations at once.

        Args:
            observations: (list[Observation])
                List of Observation instances.
        '''
        log.debug(f"Observation size: {len(self._observations)}")
        for obs in observations:
            self.add_observation(obs.x, obs.y)
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
        (return the value in objective space, use 'Y_physical'
        for return the objective in physical space)

        Returns:
            list[torch.Tensor]: 
                List of tensors, one per objective, containing 
                the corresponding objective values.        
        '''
        if not self._observations:
            log.warning("No observation available.")
        
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
        (return the position in physical space, use 
        'get_X_baseline_normalized' for the normalized space)

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
        (use 'get_X_baseline' for physical space)

        Returns:
            torch.Tensor: 
                Normalized unique input points.
        '''
        return normalize(self.get_X_baseline(), self.bounds)


    def get_ref_point(self) -> torch.Tensor:
        '''
        Compute a reference point for multi-objective optimization.

        The reference correspond to the **optimized space**.

        Returns:
            torch.Tensor: 
                Reference point vector of shape [n_obj].
        '''
        Y = torch.stack([obs.y for obs in self._observations])

        ref = Y.min(dim=0).values - 0.1 * Y.abs().max(dim=0).values

        return ref


    def get_ref_point_physical(self):
        '''
        Compute a reference point for multi-objective optimization.

        The reference correspond to the **physical space**.

        Returns:
            torch.Tensor: 
                Reference point vector of shape [n_obj].
        '''
        ref = self.get_ref_point()
        for i, obj in enumerate(self.objectives.values()):
            if obj.minimize:
                ref[i] *= -1
        return ref
    

    def compute_pareto_front(self, Y: torch.Tensor) -> torch.Tensor:
        '''
        Compute the 2D Pareto front of the given Y tensor.

        Args:
            Y: Tensor of shape [n_points, 2]

        Returns:
            Tensor of Pareto-optimal points, shape [n_pareto, 2]
        '''
        if Y.numel() == 0:
            return Y

        if Y.shape[1] != 2:
            raise ValueError("pareto_front currently supports exactly 2 objectives.")

        # Sort by objective 0 (descending = best first)
        order = torch.argsort(Y[:, 0], descending=True)
        Y_sorted = Y[order]

        pareto_mask = torch.zeros(Y_sorted.shape[0], dtype=torch.bool)

        best_y2 = -torch.inf
        for i in range(Y_sorted.shape[0]):
            y2 = Y_sorted[i, 1]
            if y2 > best_y2:
                pareto_mask[i] = True
                best_y2 = y2

        return Y_sorted[pareto_mask]


    def get_pareto_front(self) -> torch.Tensor:
        '''
        2D Pareto front in optimization space (maximize/maximize).
        '''
        Y = torch.stack([obs.y for obs in self._observations])
        if Y.numel() == 0:
            return Y

        return self.compute_pareto_front(Y)
    

    def get_pareto_front_physical(self) -> torch.Tensor:
        '''
        2D Pareto front expressed in physical objective space.
        '''
        Y_pareto_opt = self.get_pareto_front()
        if Y_pareto_opt.numel() == 0:
            return Y_pareto_opt

        return self._to_physical(Y_pareto_opt)