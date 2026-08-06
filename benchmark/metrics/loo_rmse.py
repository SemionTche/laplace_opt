import torch

from .metric import Metric
from ..analysis.benchmark_analyzer import BenchmarkAnalyzer


class LOORMSE(Metric):

    name = "LOO RMSE"

    def compute(self, analyzer: BenchmarkAnalyzer) -> float:
        "Root mean square error of the leave one out."
        mean, _, target = analyzer.loo

        return torch.sqrt(
            ( (mean - target) ** 2 ).mean()
        ).item()