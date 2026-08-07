from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from .metric import Metric
if TYPE_CHECKING:
    from ..analysis.benchmark_analyzer import BenchmarkAnalyzer


class LOORMSE(Metric):

    name = "LOO RMSE"

    def compute(self, analyzer: BenchmarkAnalyzer) -> float:
        "Root mean square error of the leave one out."
        mean, _, target = analyzer.loo

        return torch.sqrt(
            ( (mean - target) ** 2 ).mean()
        ).item()