from __future__ import annotations

from copy import deepcopy

import numpy as np
import torch

from botorch.models.transforms.outcome import Standardize
from botorch.utils.transforms import normalize

from ..experiment import BenchmarkResult
from ..metrics import METRICS
from .analysis_record import AnalysisRecord


class BenchmarkAnalyzer:
    """
    Analyze one BenchmarkResult.

    This object is intentionally temporary.

    A BenchmarkAnalyzer owns a potentially large BenchmarkResult.
    It should therefore be converted to an AnalysisRecord and then
    deleted as soon as possible.
    """
    def __init__(self, result: BenchmarkResult):
        n_points = 500

        self.result = result

        self.regret = self.regret_curve()

        self.contraction_variance = self.contraction_variance_curve(n_points=n_points)
        self.contraction_entropy = self.contraction_entropy_curve(n_points=n_points)
        self.noise = self.noise_curve()
        self.lengthscale = self.lengthscale_curve()

        self.loo = self._loo_predictions()

    @property
    def observations(self):
        return self.result.observations

    @property
    def bounds(self) -> np.ndarray:
        return np.asarray( self.result.problem["bounds"] )

    @property
    def diagonal(self):
        """Diagonal length in input space."""
        bounds = self.bounds
        return np.linalg.norm( bounds[1] - bounds[0] )

    @property
    def minimize(self) -> bool:
        """
        Objective direction.
        """
        objective = next(
            iter(
                self.result.problem["objectives"].values()
            )
        )
        return objective["minimize"]

    @property
    def y_values(self) -> np.ndarray:
        """
        Objective values in physical space.
        """
        return np.asarray(
            [
                obs["y_physical"][0]
                for obs in self.observations
            ]
        )

    @property
    def optimum_obj(self) -> float:
        """True optimum objective value."""
        return float( self.result.problem["optimum_obj"] )

    @property
    def optimum_input(self)-> np.ndarray:
        """True optimum location."""
        return np.asarray( self.result.problem["optimum_input"] )

    def best_curve(self) -> np.ndarray:
        """Best objective found so far."""
        y = self.y_values

        if self.minimize:
            return np.minimum.accumulate(y)
        
        return np.maximum.accumulate(y)

    def regret_curve(self) -> np.ndarray:
        """Simple regret evolution."""
        return np.abs( self.best_curve() - self.optimum_obj )


    def regret_instantaneous(self) -> np.ndarray:
        """Regret of every evaluation."""
        if self.minimize:
            return self.y_values - self.optimum_obj

        return self.optimum_obj - self.y_values


    def build_model(self, iteration=-1,):

        # snap = self.result.model_history[iteration]

        # model = deepcopy(
        #     snap.model
        # )
        # model.eval()

        model = self.result.model_history[iteration].model
        model.eval()

        return model


    def _loo_predictions(self, iteration: int=-1) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Leave one out method.
        
            Args:
                iteration (int):
                    The model iteration.
            
            Return:
                means (Tensor): the expected value of the prediction
                variances (Tensor): the variance of the prediction
                targets (Tensor): the sampled point
        """
        snap = self.result.model_history[iteration]
        model = self.build_model(iteration)

        # For now: only first objective
        gp = model.models[0]

        X = snap.train_X
        Y = snap.train_Y

        means, variances = [], []
        targets = []
        n = len(X)

        with torch.inference_mode():

            for i in range(n):
                X_train = torch.cat(
                    [
                        X[:i],
                        X[i+1:]
                    ]
                )

                X_train_norm = normalize(
                    X_train, torch.Tensor(self.bounds)
                )

                Y_train = torch.cat(
                    [
                        Y[:i],
                        Y[i+1:]
                    ]
                )

                loo_gp = gp.__class__(
                    train_X=X_train_norm, #X_train,
                    train_Y=Y_train,
                    outcome_transform=Standardize(m=1)
                )

                # loo_gp.load_state_dict(
                #     gp.state_dict()
                # )

                loo_gp.eval()

                X_norm = normalize( X[i:i+1], torch.Tensor(self.bounds) )
                posterior = loo_gp.posterior( X_norm )

                means.append( posterior.mean.squeeze().detach().cpu() )
                variances.append( posterior.variance.squeeze().detach().cpu() )
                targets.append( Y[i].squeeze().detach().cpu() )

                del loo_gp      # remove for memory space
                del posterior

        return (
            torch.stack(means),
            torch.stack(variances),
            torch.stack(targets),
        )


    def lengthscale_curve(self) -> np.ndarray:

        curve = []
        n = len(self.result.model_history)

        with torch.inference_mode():

            for i in range(n):
                model = self.build_model(i)

                gp = model.models[0]

                curve.append(
                    gp.covar_module.lengthscale
                    .detach()
                    .cpu()
                    .numpy()
                )

        return np.asarray(curve)


    def noise_curve(self) -> np.ndarray:

        curve = []
        n = len(self.result.model_history)

        with torch.inference_mode():

            for i in range(n):
                model = self.build_model(i)

                gp = model.models[0]

                curve.append(
                    gp.likelihood.noise.item()
                )

        return np.asarray(curve)


    def contraction_variance_curve(self, n_points: int=500) -> np.ndarray:
        """
        Integrated posterior variance.

            Returns:
                curve (ndarray) :
                    Average posterior variance over the design space
                    at every BO iteration.
        """
        bounds = torch.tensor(
            self.bounds,
            dtype=torch.double,
        )
        dim = bounds.shape[1]

        # fixed MC points for every iteration
        X = torch.rand( n_points, dim, dtype=torch.double )

        curve = []
        n = len(self.result.model_history)

        with torch.inference_mode():

            for i in range(n):
                model = self.build_model(i)
                post = model.posterior(X)

                curve.append(
                    post.variance.mean().item()
                )

        return np.asarray(curve)


    def contraction_entropy_curve(self, n_points: int=500) -> np.ndarray:
        """
        Integrated posterior entropy.

            Returns:
                curve (ndarray) :
                    Average posterior entropy over the design 
                    space at every BO iteration.
        """
        bounds = torch.tensor(
            self.bounds,
            dtype=torch.double,
        )
        dim = bounds.shape[1]

        # fixed MC points for every iteration
        X = torch.rand( n_points, dim, dtype=torch.double )

        curve = []
        n = len(self.result.model_history)

        with torch.inference_mode():

            for i in range(n):
                model = self.build_model(i)
                post = model.posterior(X)

                cts = 2 * torch.pi * torch.e
                entropy = 0.5 * torch.log( cts * post.variance )

                curve.append(
                    entropy.mean().item()
                )

        return np.asarray(curve)


    def contraction_variance_rate(self, n_points: int=500) -> np.ndarray:
        curve = self.contraction_variance_curve(n_points=n_points)
        curve = np.maximum(curve, 1e-14)
        t = np.arange(len(curve))
        slope, intercept = np.polyfit( t, np.log(curve), 1 )

        return - slope


    def summary(self) -> dict[str, float | int | str]:
        """Return the summary of the analyzer as dictionary."""
        sum = {
            "function": self.result.function_name,

            "strategy": self.result.strategy,

            "acquisition": self.result.acquisition,

            "seed": self.result.seed,

            "evaluations": len(self.result),
        }

        for metric in METRICS.values():

            sum[ metric.name ] = metric.compute(analyzer=self)

            if metric.relative_name is not None:
                sum[ metric.relative_name ] = metric.compute_relative(analyzer=self)

        return sum


    def to_record(self) -> AnalysisRecord:
        """
        Convert this expensive BenchmarkAnalyzer into a lightweight
        AnalysisRecord.

        After this method returns, the BenchmarkAnalyzer can be deleted.
        """

        metrics = self.summary()

        # Remove metadata from the metrics dictionary. (it's already in result)
        for key in (
            "function",
            "strategy",
            "acquisition",
            "seed",
            "evaluations",
        ):
            metrics.pop(key, None)

        curves = {
            "regret_curve":
                np.asarray(self.regret).copy(),

            "noise_curve":
                np.asarray(self.noise).copy(),

            "contraction_variance_curve":
                np.asarray(
                    self.contraction_variance
                ).copy(),

            "contraction_entropy_curve":
                np.asarray(
                    self.contraction_entropy
                ).copy(),

            "lengthscale_curve":
                np.asarray(self.lengthscale).copy(),
        }

        loo = tuple(
            x.detach()
            .cpu()
            .numpy()
            .copy()
            for x in self.loo
        )

        return AnalysisRecord(
            function=self.result.function_name,
            strategy=self.result.strategy,
            acquisition=self.result.acquisition,
            seed=self.result.seed,
            evaluations=len(self.result),
            metrics=metrics,
            curves=curves,
            loo=loo,
        )