from __future__ import annotations

from typing import TYPE_CHECKING
import numpy as np

from .metric import Metric
if TYPE_CHECKING:
    from ..analysis.benchmark_analyzer import BenchmarkAnalyzer


class DistanceToOptimum(Metric):

    name = "distance_x"
    relative_name = "distance_x_rel"

    def compute(self, analyzer: BenchmarkAnalyzer):
        """
        Minimum distance in X space between any sampled point
        achieving the best objective value and any true optimum input.
        """

        regrets = analyzer.regret_curve()
        best_regret = np.min(regrets)

        # All observations achieving the minimum regret
        best_ids = np.flatnonzero(np.isclose(regrets, best_regret))

        sampled_x = np.asarray(
            [analyzer.observations[i]["x"] for i in best_ids]
        )                       # shape (n_best, d)

        optimum_x = np.asarray(
            analyzer.optimum_input
        )                       # shape (n_opt, d)

        # Pairwise distances
        diff = sampled_x[:, None, :] - optimum_x[None, :, :]
        dist = np.linalg.norm(diff, axis=-1)
        # print(f"distance verif {analyzer.result.function_name}")
        # print(f"sampled_x = {sampled_x}")
        # print(f"optimum_x = {optimum_x}")
        # print(f"diff = {diff}")
        # print(f"dist = {dist}")
        # print(f"min = {np.min(dist)}")

        return np.min(dist)

    # def compute(self, analyzer: BenchmarkAnalyzer):
    #     """
    #     Distance in X space between best position
    #     found and true input optimum.
    #     """
    #     best_id = np.argmin(
    #         analyzer.regret_curve()
    #     )

    #     x = np.asarray(
    #         analyzer.observations[best_id]["x"]
    #     )

    #     print("distance verif")

    #     dist = [
    #         np.linalg.norm(
    #             x - xi
    #         )
    #         for xi in analyzer.optimum_input
    #     ]
    #     print(f"x = {x}, {analyzer.optimum_input}, dist = {dist}")
    #     x_min = np.min(dist)
    #     print(f"x_min = x_min")

    #     # dist = np.minimum([x - xi for xi in analyzer.optimum_input])

    #     # dist = np.linalg.norm(
    #     #     x - analyzer.optimum_input
    #     # )
    #     # print(f"x = {x}, {analyzer.optimum_input}, dist = {dist}")

    #     return dist

    def compute_relative(self, analyzer: BenchmarkAnalyzer):
        """
        Relative distance in X space between best 
        position found and true input optimum.

        (Normalized by the input diagonal)
        """
        return (
            self.compute(analyzer)
            /
            analyzer.diagonal
        )