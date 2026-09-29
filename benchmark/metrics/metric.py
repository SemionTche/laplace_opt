from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..analysis.benchmark_analyzer import BenchmarkAnalyzer


class Metric(ABC):

    name: str
    relative_name: str | None = None

    @abstractmethod
    def compute(self, analyzer: BenchmarkAnalyzer) -> float | int:
        """Compute the metric."""

    def compute_relative(self, analyzer: BenchmarkAnalyzer) -> float | int:
        raise NotImplementedError