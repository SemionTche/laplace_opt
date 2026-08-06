import numpy as np

from .metric import Metric


class DistanceToOptimum(Metric):

    name = "distance_x"
    relative_name = "distance_x_rel"

    def compute(self, analyzer):

        best_id = np.argmin(
            analyzer.regret_curve()
        )

        x = np.asarray(
            analyzer.observations[best_id]["x"]
        )

        return np.linalg.norm(
            x - analyzer.optimum_input
        )

    def compute_relative(self, analyzer):

        return (
            self.compute(analyzer)
            /
            analyzer.diagonal
        )