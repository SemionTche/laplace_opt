"""
benchmark_result.py

Container storing the complete outcome of one benchmark optimization run.

A BenchmarkResult is not intended to resume an optimization.
It stores only the information required to analyze and compare
benchmark experiments.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import hashlib
import json
import time

import torch
import pandas as pd


@dataclass(slots=True)
class BenchmarkResult:

    # --------------------------------------------------
    # Benchmark identity
    # --------------------------------------------------

    benchmark_name: str

    function_name: str

    strategy: str

    acquisition: str

    seed: int

    n_inputs: int

    n_objectives: int


    # --------------------------------------------------
    # Timing
    # --------------------------------------------------

    started: float = field(default_factory=time.time)

    finished: float | None = None

    elapsed_time: float | None = None


    # --------------------------------------------------
    # Benchmark data
    # --------------------------------------------------

    observations: list[dict] = field(default_factory=list)


    # --------------------------------------------------
    # Static information
    # --------------------------------------------------

    problem: dict = field(default_factory=dict)


    # --------------------------------------------------
    # Derived results
    # --------------------------------------------------

    metrics: dict = field(default_factory=dict)


    # --------------------------------------------------
    # Run information
    # --------------------------------------------------

    metadata: dict = field(default_factory=dict)


    mode: str = field(default_factory=str)

    # ==================================================

    def finish(self):

        self.finished = time.time()

        self.elapsed_time = (
            self.finished - self.started
        )


    # ==================================================

    def add_observation(
        self,
        x: torch.Tensor,
        y_physical: torch.Tensor,
        y_opt: torch.Tensor,
        iteration: int,
        is_init: bool,
        shot_number: int,
        batch: int = 0,
        candidate: int = 0):

        self.observations.append(
            {
                "iteration": int(iteration),

                "phase":
                    "initialization"
                    if is_init
                    else "optimization",

                "x":
                    torch.as_tensor(x)
                    .detach()
                    .cpu()
                    .tolist(),

                "y_physical":
                    torch.as_tensor(y_physical)
                    .detach()
                    .cpu()
                    .tolist(),

                "y_opt":
                    torch.as_tensor(y_opt)
                    .detach()
                    .cpu()
                    .tolist(),

                "shot_number":
                    int(shot_number),

                "batch":
                    int(batch),

                "candidate":
                    int(candidate),
            }
        )


    # ==================================================

    @property
    def n_evaluations(self):

        return len(self.observations)


    # ==================================================

    @property
    def dataframe(self):

        rows = []

        for obs in self.observations:

            row = {
                "iteration": obs["iteration"],
                "phase": obs["phase"],
                "shot_number": obs["shot_number"],
                "batch": obs["batch"],
                "candidate": obs["candidate"],
            }

            for i, value in enumerate(obs["x"]):
                row[f"x{i+1}"] = value

            for i, value in enumerate(obs["y_physical"]):
                row[f"y{i+1}"] = value

            rows.append(row)

        return pd.DataFrame(rows)


    # ==================================================

    @property
    def X(self):

        return torch.tensor(
            [
                obs["x"]
                for obs in self.observations
            ]
        )


    # ==================================================

    @property
    def Y(self):

        return torch.tensor(
            [
                obs["y_physical"]
                for obs in self.observations
            ]
        )


    # ==================================================

    def add_metadata(self, **kwargs):

        self.metadata.update(kwargs)


    # ==================================================

    def add_metrics(self, **kwargs):

        self.metrics.update(kwargs)


    # ==================================================

    def add_problem(self, **kwargs):

        self.problem.update(kwargs)


    # ==================================================

    def save(self, folder: Path):

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

        data = {

            "benchmark": {
                "benchmark_name": self.benchmark_name,
                "function_name": self.function_name,
                "acquisition": self.acquisition,
                "strategy": self.strategy,
                "seed": self.seed,
                "n_inputs": self.n_inputs,
                "n_objectives": self.n_objectives,
            },

            "timing": {
                "started": self.started,
                "finished": self.finished,
                "elapsed_time": self.elapsed_time,
            },

            "observations": self.observations,

            "problem": self.problem,

            "metrics": self.metrics,

            "metadata": self.metadata,

            "mode": self.mode
        }


        torch.save(
            data,
            folder / "benchmark_result.pt"
        )


    # ==================================================

    @classmethod
    def load(cls, folder: Path):

        data = torch.load(
            folder / "benchmark_result.pt"
        )

        obj = cls(
            **data["benchmark"]
        )

        obj.started = data["timing"]["started"]
        obj.finished = data["timing"]["finished"]
        obj.elapsed_time = data["timing"]["elapsed_time"]

        obj.observations = data["observations"]

        obj.problem = data["problem"]

        obj.metrics = data["metrics"]

        obj.metadata = data["metadata"]

        return obj


    # ==================================================

    def summary(self):

        return (
            "=" * 60
            + "\nBenchmark Result\n"
            + "=" * 60
            + f"\nFunction     : {self.function_name}"
            + f"\nStrategy     : {self.strategy}"
            + f"\nAcquisition  : {self.acquisition}"
            + f"\nSeed         : {self.seed}"
            + f"\nEvaluations  : {self.n_evaluations}"
            + f"\nElapsed time : {self.elapsed_time:.2f}s"
            + f"\nMode         : {self.mode}"
        )


    # ==================================================

    def __len__(self):

        return len(self.observations)


    def __repr__(self):

        return self.summary()