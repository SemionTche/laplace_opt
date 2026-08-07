from __future__ import annotations

from typing import TYPE_CHECKING
import numpy as np

from .metric import Metric
if TYPE_CHECKING:
    from ..analysis.benchmark_analyzer import BenchmarkAnalyzer
from ..bench_utils.normalize import norm_curve


class TimeToEpsilon(Metric):
    name = "time_to_eps"
    relative_name = "time_to_eps_rel"

    def compute(self, analyzer: BenchmarkAnalyzer, epsilon: float=0.01) -> int | None:
        """Number of evaluations needed to reach epsilon optimality."""
        regret = analyzer.regret_curve()
        idx = np.where( regret <= epsilon )[0]

        if len(idx) == 0:
            return None

        return int(idx[0])


    def compute_relative(self, analyzer: BenchmarkAnalyzer, epsilon_rel: float=0.05) -> int | None:
        """Number of evaluations needed to reach epsilon optimality (in %)."""
        # regret_rel = analyzer.regret_curve_relative()
        # idx = np.where( regret_rel <= epsilon_rel )[0]
        rel = norm_curve(
            curve=analyzer.regret_curve(),
            normalization="relative"
        )
        idx = np.where( rel <= epsilon_rel )[0]

        if len(idx) == 0:
            return None

        return int(idx[0])