from __future__ import annotations

from copy import deepcopy
import numpy as np

import torch
from torch.distributions import Normal

from ..benchmark_result import BenchmarkResult
from ..metrics import METRICS



class BenchmarkAnalyzer:
    """
    Analyze one BenchmarkResult.

    This class computes BO metrics
    from one optimization run.
    """
    def __init__(self, result: BenchmarkResult):
        self.result = result


    @property
    def observations(self):
        return self.result.observations

    @property
    def bounds(self) -> np.ndarray:
        return np.asarray(
            self.result.problem["bounds"]
        )

    @property
    def diagonal(self):
        """Diagonal length in input space."""
        bounds = self.bounds

        return np.linalg.norm(
            bounds[1] - bounds[0]
        )

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
        """
        True optimum objective value.
        """
        return float(
            self.result.problem["optimum_obj"]
        )

    @property
    def optimum_input(self)-> np.ndarray:
        """
        True optimum location.
        """
        return np.asarray(
            self.result.problem["optimum_input"]
        )

    @property
    def initial_regret(self) -> float:
        return self.regret_curve()[0]

    @property
    def final_model(self):
        return self.result.model_history[-1]


    def best_curve(self) -> np.ndarray:
        """
        Best objective found so far.
        """
        y = self.y_values

        if self.minimize:

            return np.minimum.accumulate(y)

        else:

            return np.maximum.accumulate(y)


    def regret_curve(self) -> np.ndarray:
        """
        Simple regret evolution.
        """
        return np.abs(
            self.best_curve()
            -
            self.optimum_obj
        )


    def regret_curve_relative(self) -> np.ndarray:

        r = self.regret_curve()

        r0 = r[0]

        if r0 == 0:

            return np.zeros_like(r)

        return r / r0


    def simple_regret(self) -> float:
        """
        Final regret.
        """
        return float(
            self.regret_curve()[-1]
        )


    def simple_regret_relative(self) -> float:

        return float(
            self.regret_curve_relative()[-1]
        )


    def instantaneous_regret(self) -> np.ndarray:
        """
        Regret of every evaluation.
        """
        if self.minimize:

            return (
                self.y_values
                -
                self.optimum_obj
            )

        else:

            return (
                self.optimum_obj
                -
                self.y_values
            )



    def area_under_regret_curve(self):
        """
        Integral of regret curve.
        """
        return float(
            np.trapezoid(
                self.regret_curve()
            )
        )


    def area_under_regret_curve_relative(self) -> float:
        return float(
            np.trapezoid(
                self.regret_curve_relative()
            )
            /
            (len(self.regret_curve()) - 1)
        )

    def time_to_epsilon(self, epsilon=0.01) -> int | None:
        """
        Number of evaluations needed
        to reach epsilon optimality.
        """
        indexes = np.where(
            self.regret_curve() <= epsilon
        )[0]

        if len(indexes) == 0:
            return None

        return int(indexes[0])


    def time_to_relative_epsilon(self, epsilon=0.05) -> int | None:

        regret = self.regret_curve_relative()

        idx = np.where(
            regret <= epsilon
        )[0]

        if len(idx) == 0:

            return None

        return int(idx[0])


    def distance_to_optimum(self) -> float:
        """
        Distance in X space between
        best found point and true optimum.
        """
        best_id = np.argmin(
            self.regret_curve()
        )

        x_found = np.asarray(
            self.observations[best_id]["x"]
        )

        return float(
            np.linalg.norm(
                x_found - self.optimum_input
            )
        )


    def distance_to_optimum_relative(self):

        return (
            self.distance_to_optimum()
            /
            self.diagonal
        )


    def build_model(self, iteration=-1,):

        snap = self.result.model_history[iteration]

        model = deepcopy(
            snap.model
        )

        model.eval()

        return model


    def _loo_predictions(self, iteration=-1):

        snap = self.result.model_history[iteration]

        model = self.build_model(iteration)

        # For now: only first objective
        gp = model.models[0]

        # print(f"snap x shape = {snap.train_X.shape}, snap y shape = {snap.train_Y.shape}")

        X = snap.train_X

        Y = snap.train_Y

        means = []
        variances = []
        targets = []

        n = len(X)


        for i in range(n):

            X_train = torch.cat(
                [
                    X[:i],
                    X[i+1:]
                ]
            )

            Y_train = torch.cat(
                [
                    Y[:i],
                    Y[i+1:]
                ]
            )

            # print(f"train X shape : {X_train.shape}, Y train shape = {Y_train.shape}")
            loo_gp = gp.__class__(
                train_X=X_train,
                train_Y=Y_train,
            )


            # loo_gp.load_state_dict(
            #     gp.state_dict()
            # )

            loo_gp.eval()


            posterior = loo_gp.posterior(
                X[i:i+1]
            )


            means.append(
                posterior.mean.squeeze()
            )


            variances.append(
                posterior.variance.squeeze()
            )


            targets.append(
                Y[i].squeeze()
            )


        return (
            torch.stack(means),
            torch.stack(variances),
            torch.stack(targets),
        )


    def lengthscale_curve(self):

        curve = []

        for i in range(len(self.result.model_history)):

            model = self.build_model(i)

            gp = model.models[0]

            curve.append(
                gp.covar_module.lengthscale
                .detach()
                .cpu()
                .numpy()
            )

        return np.asarray(curve)


    def noise_curve(self):

        curve = []

        for i in range(len(self.result.model_history)):

            model = self.build_model(i)

            gp = model.models[0]

            curve.append(
                gp.likelihood.noise.item()
            )

        return np.asarray(curve)



    def loo_rmse(self):

        mean, _, target = self._loo_predictions()

        return torch.sqrt(

            torch.mean(

                (mean-target)**2

            )

        ).item()


    def loo_nlpd(self):
        # lower is better, Perfect GP -> small NLPD, overconfident -> huge NLPD
        mean, var, target = self._loo_predictions()

        std = torch.sqrt(

            torch.clamp(

                var,

                min=1e-12,

            )

        )

        dist = Normal(

            mean,

            std,

        )

        return (

            -dist.log_prob(

                target

            )

            .mean()

            .item()

        )


    def coverage95(self):

        mean, var, target = self._loo_predictions()

        std = torch.sqrt(var)

        lower = mean - 1.96*std

        upper = mean + 1.96*std

        inside = (

            (target >= lower)

            &

            (target <= upper)

        )

        return inside.float().mean().item()



    def posterior_contraction(self):

        values = []

        for i in range(len(self.result.model_history)):

            model = self.build_model(i)

            X = model.models[0].train_inputs[0]

            post = model.posterior(X)

            values.append(
                post.variance.mean().item()
            )

        return values





    def summary(self):

        return {

            "function":
                self.result.function_name,


            "strategy":
                self.result.strategy,


            "acquisition":
                self.result.acquisition,


            "seed":
                self.result.seed,


            "evaluations":
                len(self.result),


            # "simple_regret":
            #     self.simple_regret(),


            # "auc_regret":
            #     self.area_under_regret_curve(),


            # "time_to_eps":
            #     self.time_to_epsilon(),


            # "distance_x":
            #     self.distance_to_optimum(),


            "simple_regret":
                self.simple_regret(),

            "simple_regret_rel":
                self.simple_regret_relative(),

            "auc_regret":
                self.area_under_regret_curve(),

            "auc_regret_rel":
                self.area_under_regret_curve_relative(),

            "distance_x":
                self.distance_to_optimum(),

            "distance_x_rel":
                self.distance_to_optimum_relative(),

            "time_to_eps":
                self.time_to_relative_epsilon(),

            "LOO RMSE":
                self.loo_rmse(),

            "LOO NLPD":
                self.loo_nlpd(),

            "Coverage":
                self.coverage95(),

            "Post Constraction":
                self.posterior_contraction(),

        }