from __future__ import annotations

from typing import TYPE_CHECKING

from .metric import Metric
if TYPE_CHECKING:
    from ..analysis.benchmark_analyzer import BenchmarkAnalyzer


class NoiseMean(Metric):

    name = "Noise_mean"

    def compute(self, analyzer: BenchmarkAnalyzer):
        """Compute the mean of the noise evolution."""
        return analyzer.noise_curve().mean()


class NoiseStd(Metric):

    name = "Noise_std"

    def compute(self, analyzer: BenchmarkAnalyzer):
        """Compute the std of the noise evolution."""
        return analyzer.noise_curve().std()
