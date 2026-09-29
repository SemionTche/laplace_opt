from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from .metric import Metric
if TYPE_CHECKING:
    from ..analysis.benchmark_analyzer import BenchmarkAnalyzer
from ..bench_utils.normalize import norm_curve


class SimpleRegret(Metric):

    name = "simple_regret"
    relative_name = "simple_regret_rel"

    def compute(self, analyzer: BenchmarkAnalyzer) -> float:
        return float( analyzer.regret[-1] )

    def compute_relative(self, analyzer: BenchmarkAnalyzer) -> float:
        # return float(
        #     analyzer.regret_curve_relative()[-1]
        # )
        rel = norm_curve(
            curve=analyzer.regret,
            normalization="relative"
        )
        return rel[-1]


class CumulativeRegret(Metric):

    name = "Cumulative regret"
    relative_name = "Relative cumulative regret"

    def compute(self, analyzer: BenchmarkAnalyzer) -> float:
        return np.sum( analyzer.regret )

    def compute_relative(self, analyzer: BenchmarkAnalyzer) -> float:
        rel = norm_curve(
            curve=analyzer.regret,
            normalization="relative"
        )
        return np.sum( rel )


class AreaUnderRegretCurve(Metric):
    name = "aurc"
    relative_name = "aurc_rel"


    def compute(self, analyzer: BenchmarkAnalyzer) -> float:
        """Integral of instantaneous regret curve."""
        return float(
            np.trapezoid(
                analyzer.regret_instantaneous()
            )
        )

    def compute_relative(self, analyzer: BenchmarkAnalyzer) -> float:
        """Integral of relative instantaneous regret curve normalized by number of iteration."""
        # return float(
        #     np.trapezoid(
        #         analyzer.regret_curve_relative()
        #     )
        #     /
        #     (len(analyzer.regret_curve()) - 1)
        # )
        rel = norm_curve(
            curve=analyzer.regret_instantaneous(),
            normalization="relative"
        )
        area = np.trapezoid(rel) / (len(rel) - 1)
        return float(area)
