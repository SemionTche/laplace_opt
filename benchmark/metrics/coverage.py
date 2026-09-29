from __future__ import annotations

from typing import TYPE_CHECKING
import torch
from torch.distributions import Normal

from .metric import Metric
if TYPE_CHECKING:
    from ..analysis.benchmark_analyzer import BenchmarkAnalyzer

class Coverage(Metric):

    name = "coverage"

    def compute(self, analyzer: BenchmarkAnalyzer, percent=0.95):
        """
        Compute the empirical coverage of Gaussian prediction intervals.

        A two-sided prediction interval is constructed for each prediction using
        the requested confidence level ``percent``. The returned value is the
        fraction of targets lying inside their corresponding prediction interval.

        Returns:
            The empirical coverage, i.e. the proportion of target values that
            fall within the prediction intervals.
        """
        mean, var, target = analyzer.loo
        std = torch.sqrt(var)

        z = Normal(0., 1.).icdf(
            torch.Tensor( [(1 + percent) / 2] )
        )
        lower = mean - z * std
        upper = mean + z * std

        inside = (
            (target >= lower) & (target <= upper)
        )

        return inside.float().mean().item()