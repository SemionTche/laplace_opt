import torch
from torch.distributions import Normal

from .metric import Metric
from ..analysis.benchmark_analyzer import BenchmarkAnalyzer


class LOONLPD(Metric):

    name = "LOO NLPD"

    def compute(self, analyzer: BenchmarkAnalyzer):
        """Negative log probability density."""
        mean, var, target = analyzer.loo

        std = torch.sqrt(
            torch.clamp(
                var,
                min=1e-12,
            )
        )

        dist = Normal(mean, std)

        return (
            -dist.log_prob(target)
            .mean()
            .item()
        )