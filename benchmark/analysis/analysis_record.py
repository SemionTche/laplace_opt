from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class AnalysisRecord:
    """
    Lightweight, persistent representation of one analyzed benchmark.

    IMPORTANT:
        This class must never contain a BenchmarkResult, GP model,
        posterior, or other large PyTorch object.

    Only data required for later analysis/plotting is kept.
    """

    function: str
    strategy: str
    acquisition: str
    seed: int

    evaluations: int

    metrics: dict[str, float | int | str] = field(default_factory=dict)

    curves: dict[str, np.ndarray] = field(default_factory=dict)

    loo: tuple[np.ndarray, np.ndarray, np.ndarray] = field(default_factory=tuple[np.ndarray, np.ndarray, np.ndarray])

    def summary(self) -> dict[str, Any]:
        """
        Return one row suitable for a pandas DataFrame.
        """

        row = {
            "function": self.function,
            "strategy": self.strategy,
            "acquisition": self.acquisition,
            "seed": self.seed,
            "evaluations": self.evaluations,
        }

        row.update(self.metrics)

        return row