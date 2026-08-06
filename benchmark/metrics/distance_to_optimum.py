import numpy as np

from .metric import Metric

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

        return np.linalg.norm(
            x - analyzer.optimum_input
        )


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