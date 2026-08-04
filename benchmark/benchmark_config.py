"""
benchmark_config.py

Configuration objects used by the benchmarking framework.

These classes are completely independent from the optimizer.
Their purpose is only to describe which benchmark has to be executed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable
import copy

from .functions.base import TestFunction

@dataclass(slots=True)
class BenchmarkConfig:
    """
    Configuration of one benchmark campaign.

    One BenchmarkConfig may execute many optimization runs
    (typically one run per random seed and target function).

    Parameters
    ----------
    name: (str)
        Name of the experiment.

    optimizer_form: (dict)
        Human-readable OPT_FORM dictionary.

    target_functions: (list[callable])
        List of callables used by the dummy server.

    iterations: (int)
        Number of BO iterations after initialization.

    seeds: (list[int])
        List of random seeds.

    output_folder: (str)
        Root folder where results are saved.

    notes:
        Free text for benchmark summary.
    """

    name: str

    optimizer_form: dict

    target_functions: list[Callable]

    iterations: int = 40

    seeds: list[int] = field(default_factory=lambda: [0])

    output_folder: Path = Path("benchmark/results")

    notes: str = ""

    # tags: list[str] = field(default_factory=list)


    @property
    def n_runs(self) -> int:
        return len(self.seeds)

    @property
    def is_multi_objective(self) -> bool:
        return len(self.optimizer_form["obj"]) > 1

    @property
    def acquisition_name(self) -> str:

        if not self.optimizer_form["opt"]["enabled"]:
            return "None"

        return next(
            iter(
                self.optimizer_form["opt"]["pipeline"]["acquisition"].keys()
            )
        )

    @property
    def strategy_name(self) -> str:

        if not self.optimizer_form["opt"]["enabled"]:
            return "None"

        return next(
            iter(
                self.optimizer_form["opt"]["pipeline"]["strategy"].keys()
            )
        )

    @property
    def function_names(self) -> list[str]:
        names = []

        for target_function in self.target_functions:

            if hasattr(target_function, "name"):
                names.append(target_function.name)

            else:
                names.append(target_function.__name__)

        return names


    def build_opt_form(self, seed: int, target_function: TestFunction) -> dict:
        """
        Return a deep copy of OPT_FORM with the correct seed inserted.

        The original OPT_FORM is never modified.
        """

        form = copy.deepcopy(self.optimizer_form)

        # initialization seed
        init_name = next(iter(form["init"]))

        form["init"][init_name]["seed"] = seed

        if form["opt"]["enabled"]:

            strat_name = next(
                iter(
                    form["opt"]["pipeline"]["strategy"]
                )
            )

            form["opt"]["pipeline"]["strategy"][strat_name]["seed"] = seed

        # adapt the input to the target function
        if hasattr(target_function, "name"):
            func_name = target_function.name
        else:
            func_name = target_function.__name__

        form["target_function"] = {
            "name": func_name,
            "bounds": target_function.bounds.tolist(),
            "minimize": target_function.minimize
        }

        for i, key in enumerate(form["inputs"].keys()):
            form["inputs"][key]["bounds"] = target_function.bounds[:, i].tolist()


        # adapt the objective to the target function
        for i, key in enumerate(form["obj"].keys()):
            form["obj"][key]["minimize"] = target_function.minimize

        return form


    def run_folder(self, function_name: str, seed: int) -> Path:
        """
        Folder where one optimization run is saved.
        """

        return (
            self.output_folder
            / self.name
            / function_name
            / f"seed_{seed:04d}"
        )


    def summary(self) -> str:

        txt = []

        txt.append("=" * 60)
        txt.append("Benchmark configuration")
        txt.append("=" * 60)

        txt.append(f"Name            : {self.name}")
        txt.append(f"Function        : {self.function_names}")
        txt.append(f"Acquisition     : {self.acquisition_name}")
        txt.append(f"Strategy        : {self.strategy_name}")
        txt.append(f"Iterations      : {self.iterations}")
        txt.append(f"Runs            : {self.n_runs}")
        txt.append(f"Seeds           : {self.seeds}")
        txt.append(f"Output folder   : {self.output_folder}")

        if self.notes:
            txt.append("")
            txt.append("Notes")
            txt.append("-----")
            txt.append(self.notes)

        return "\n".join(txt)