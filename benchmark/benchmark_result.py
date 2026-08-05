from __future__ import annotations


from dataclasses import dataclass, field
from copy import deepcopy
from pathlib import Path

import time
import pandas as pd

import torch
from botorch.models.model import Model

from .bench_utils.model_snapshot import ModelSnapshot


@dataclass(slots=True)
class BenchmarkResult:
    """
    Container storing the complete outcome of one experiment.
    """
    ### Benchmark
    benchmark_name: str

    function_name: str

    strategy: str

    acquisition: str

    seed: int

    n_inputs: int

    n_objectives: int


    ### Timing
    started: float = field(default_factory=time.time)

    finished: float | None = None

    elapsed_time: float | None = None

    ### data
    observations: list[dict] = field(default_factory=list)

    ### problem
    problem: dict = field(default_factory=dict)

    ### metrics
    # metrics: dict = field(default_factory=dict)

    ### metadata
    metadata: dict = field(default_factory=dict)

    ### surrogate history
    model_history: list[ModelSnapshot] = field(default_factory=list)

    ### acquisition history
    acquisition_history: list[dict] = field(default_factory=list)


    @property
    def n_evaluations(self) -> int:
        return len(self.observations)

    @property
    def dataframe(self) -> pd.DataFrame:
        """Experiment dataframe."""
        rows = []

        for obs in self.observations:

            row = {
                "iteration": obs["iteration"],
                "phase": obs["phase"],
                "shot_number": obs["shot_number"],
            }

            for i, value in enumerate(obs["x"]):
                row[f"x{i+1}"] = value

            for i, value in enumerate(obs["y_physical"]):
                row[f"y{i+1}"] = value

            rows.append(row)

        return pd.DataFrame(rows)

    @property
    def X(self) -> torch.Tensor:
        "Physical space."
        return torch.tensor( [obs["x"] for obs in self.observations] )

    @property
    def Y(self) -> torch.Tensor:
        "Physical space."
        return torch.tensor( [obs["y_physical"] for obs in self.observations] )


    def finish(self) -> None:

        self.finished = time.time()

        self.elapsed_time = (
            self.finished - self.started
        )

    def add_observation(self,
                        x: torch.Tensor,
                        y_physical: torch.Tensor,
                        y_opt: torch.Tensor,
                        iteration: int,
                        is_init: bool,
                        shot_number: int,) -> None:

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
            }
        )

    def add_metadata(self, **kwargs) -> None:
        self.metadata.update(kwargs)

    # def add_metrics(self, **kwargs) -> None:
    #     self.metrics.update(kwargs)

    def add_problem(self, **kwargs) -> None:
        self.problem.update(kwargs)

    def add_model_snapshot(self,
                           iteration: int,
                           model: Model,
                           train_X: torch.Tensor,
                           train_Y: torch.Tensor):

        self.model_history.append(
            ModelSnapshot(
                iteration=iteration,
                model=model,
                train_X=train_X.detach().clone(),
                train_Y=train_Y.detach().clone(),
            )
        )

    def add_acquisition_state(self,
                              iteration: int,
                              acquisition,):
        """
        Add acquisition parameters.
        """
        self.acquisition_history.append(
            {
                "iteration": iteration,

                "acquisition_class":
                    acquisition.__class__.__module__
                    + "."
                    + acquisition.__class__.__qualname__,

                "state_dict":
                    deepcopy(acquisition.state_dict()),
            }
        )


    def save(self, folder: Path) -> None:
        """
        Save the result of an experiment in a 
        'benchmark_result.pt' file.
        """
        folder.mkdir(parents=True, exist_ok=True)

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
            # "metrics": self.metrics,
            "metadata": self.metadata,
            "model_history": self.model_history,
            "acquisition_history": self.acquisition_history,
        }

        torch.save(data, folder / "benchmark_result.pt")


    @classmethod
    def load(cls, folder: Path) -> BenchmarkResult:
        """
        Load the BenchmarkResult contained in the given folder.
        """
        data = torch.load(
            folder / "benchmark_result.pt",
            map_location="cpu",
            weights_only=False
        )
        # create the benchmark result object
        obj = cls(
            **data["benchmark"]
        )

        # fill the fields
        obj.started = data["timing"]["started"]
        obj.finished = data["timing"]["finished"]
        obj.elapsed_time = data["timing"]["elapsed_time"]

        obj.observations = data["observations"]

        obj.problem = data["problem"]

        # obj.metrics = data["metrics"]

        obj.metadata = data["metadata"]

        obj.model_history = data["model_history"]

        obj.acquisition_history = data["acquisition_history"]

        return obj


    def summary(self) -> str:
        """
        Result summary.
        """
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
        )

    def __len__(self):
        return len(self.observations)

    def __repr__(self):
        return self.summary()