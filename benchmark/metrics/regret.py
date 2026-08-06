import numpy as np

from .metric import Metric
from ..analysis.benchmark_analyzer import BenchmarkAnalyzer


class SimpleRegret(Metric):

    name = "simple_regret"
    relative_name = "simple_regret_rel"

    def compute(self, analyzer: BenchmarkAnalyzer) -> float:

        return float(
            analyzer.regret_curve()[-1]
        )

    def compute_relative(self, analyzer: BenchmarkAnalyzer) -> float:

        return float(
            analyzer.regret_curve_relative()[-1]
        )


class AreaUnderRegretCurve(Metric):
    name = "aurc"
    relative_name = "aurc_rel"


    def compute(self, analyzer: BenchmarkAnalyzer) -> float:
        """Integral of regret curve."""
        return float(
            np.trapezoid(
                analyzer.regret_curve()
            )
        )

    def compute_relative(self, analyzer: BenchmarkAnalyzer) -> float:
        """Integral of relative regret curve normalized by number of iteration."""
        return float(
            np.trapezoid(
                analyzer.regret_curve_relative()
            )
            /
            (len(analyzer.regret_curve()) - 1)
        )