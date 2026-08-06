import numpy as np

from .metric import Metric


class FinalVarianceContraction(Metric):

    name = "Final variance contraction"
    relative_name = "Final relative variance contraction"

    def compute(self, analyzer) -> float:
        """Final posterior variance contraction."""
        curve = analyzer.contraction_variance_curve()
        return curve[-1]

    def compute_relative(self, analyzer) -> float:
        """Final relative posterior variance contraction."""
        curve = analyzer.contraction_variance_curve()
        return curve[-1] / curve[0]


class FinalEntropyContraction(Metric):

    name = "Final entropy contraction"
    relative_name = "Final relative entropy contraction"

    def compute(self, analyzer) -> float:
        """Final posterior entropy contraction."""
        curve = analyzer.contraction_entropy_curve()
        return curve[-1]

    def compute_relative(self, analyzer) -> float:
        """Final relative posterior entropy contraction."""
        curve = analyzer.contraction_entropy_curve()
        return curve[-1] / curve[0]


class HalfLifeVarianceContraction(Metric):

    name = "Half-life variance contraction"
    relative_name = "Relative half-life variance contraction"

    def compute(self, analyzer) -> int | float:
        """Half-life posterior variance contraction."""
        curve = analyzer.contraction_variance_curve()
        target = curve[0] / 2

        idx = np.where(curve <= target)[0]

        if len(idx) == 0:
            return np.inf
        
        return idx[0]

    def compute_relative(self, analyzer) -> float:
        """Half-life relative posterior variance contraction."""
        idx = self.compute(analyzer=analyzer)
        n = len(analyzer.result.model_history)
        return idx / n


class HalfLifeEntropyContraction(Metric):

    name = "Half-life entropy contraction"
    relative_name = "Relative half-life entropy contraction"

    def compute(self, analyzer) -> int | float:
        """Half-life posterior entropy contraction."""
        curve = analyzer.contraction_entropy_curve()
        target = curve[0] / 2

        idx = np.where(curve <= target)[0]

        if len(idx) == 0:
            return np.inf
        
        return idx[0]

    def compute_relative(self, analyzer) -> float:
        """Half-life relative posterior entropy contraction."""
        idx = self.compute(analyzer=analyzer)
        n = len(analyzer.result.model_history)
        return idx / n