from __future__ import annotations

import numpy as np

from ..benchmark_result import BenchmarkResult


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
    def minimize(self):

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
    def y_values(self):
        """
        Objective values observed during BO.
        """
        return np.asarray(
            [
                obs["y_physical"][0]
                for obs in self.observations
            ]
        )

    @property
    def global_value(self):
        """
        True optimum objective value.
        """
        return float(
            self.result.problem["global_value"]
        )

    @property
    def global_min(self):
        """
        True optimum location.
        """
        return np.asarray(
            self.result.problem["global_min"]
        )


    def best_curve(self):
        """
        Best objective found so far.
        """
        y = self.y_values

        if self.minimize:

            return np.minimum.accumulate(y)

        else:

            return np.maximum.accumulate(y)


    def regret_curve(self):
        """
        Simple regret evolution.
        """
        return np.abs(
            self.best_curve()
            -
            self.global_value
        )


    def simple_regret(self):
        """
        Final regret.
        """
        return float(
            self.regret_curve()[-1]
        )


    def instantaneous_regret(self):
        """
        Regret of every evaluation.
        """
        if self.minimize:

            return (
                self.y_values
                -
                self.global_value
            )

        else:

            return (
                self.global_value
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


    def time_to_epsilon(self, epsilon=0.01):
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



    def distance_to_optimum(self):
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
                x_found - self.global_min
            )
        )


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


            "simple_regret":
                self.simple_regret(),


            "auc_regret":
                self.area_under_regret_curve(),


            "time_to_eps":
                self.time_to_epsilon(),


            "distance_x":
                self.distance_to_optimum(),

        }