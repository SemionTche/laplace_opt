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
        Distance in X space between best position
        found and true input optimum.
        """
        best_id = np.argmin(
            analyzer.regret_curve()
        )

        x = np.asarray(
            analyzer.observations[best_id]["x"]
        )

        print("distance verif")

        dist = np.linalg.norm(
            x - analyzer.optimum_input
        )
        print(f"x = {x}, {analyzer.optimum_input}, dist = {dist}")

        return dist

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