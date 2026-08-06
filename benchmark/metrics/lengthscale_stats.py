from .metric import Metric

from ..analysis.benchmark_analyzer import BenchmarkAnalyzer


class LengthscaleMean(Metric):

    name = "rho_mean"

    def compute(self, analyzer: BenchmarkAnalyzer):
        """Compute the mean of the lengthscale evolution."""
        return analyzer.lengthscale_curve().mean()


class LengthscaleStd(Metric):

    name = "rho_std"

    def compute(self, analyzer: BenchmarkAnalyzer):
        """Compute the std of the lengthscale evolution."""
        return analyzer.lengthscale_curve().std()
