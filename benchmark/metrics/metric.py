from __future__ import annotations

from abc import ABC, abstractmethod


class Metric(ABC):

    name: str
    relative_name: str | None = None

    @abstractmethod
    def compute(self, analyzer):
        """Compute the metric."""

    def compute_relative(self, analyzer):
        raise NotImplementedError