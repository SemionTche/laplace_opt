from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import copy

from .functions.base import TestFunction


@dataclass(slots=True)
class BenchmarkConfig:
    """
    Benchmark configuration, gathering the parameters for the runs.

    It is used as individual config class after build_opt_form.

    One BenchmarkConfig may execute many optimization runs
    (typically one run per random seed and target function).

    Args:
        name: (str)
            Name of the benchmark.

        optimizer_form: (dict)
            Human-readable OPT_FORM dictionary.

        target_functions: (list[TestFunction])
            List of TestFunction used by the dummy server.

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

    target_functions: list[TestFunction]

    iterations: int = 40

    seeds: list[int] = field(default_factory=lambda: [0])

    output_folder: Path = Path("benchmark/results")

    notes: str = ""


    @property
    def n_runs(self) -> int:
        """Number of runs for a given target function."""
        return len(self.seeds)

    @property
    def n_func(self) -> int:
        return len(self.target_functions)

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


    def build_opt_form(self, target_function: TestFunction, seed: int) -> dict:
        """
        Return a deep copy of OPT_FORM with 
        the correct seed and target function inserted.

        The original OPT_FORM is never modified.
        """
        form = copy.deepcopy(self.optimizer_form)

        ### initialization seed
        init_name = next( iter( form["init"] ) )
        form["init"][init_name]["seed"] = seed

        ### strategy seed
        if form["opt"]["enabled"]:

            strat_name = next(
                iter(
                    form["opt"]["pipeline"]["strategy"]
                )
            )

            form["opt"]["pipeline"]["strategy"][strat_name]["seed"] = seed

        ### adapt the input to the target function
        if hasattr(target_function, "name"):
            func_name = target_function.name
        else:
            func_name = target_function.__name__

        form["target_function"] = {                  # add the target function
            "name": func_name,
            "bounds": target_function.bounds.tolist(),
            "minimize": target_function.minimize
        }

        for i, key in enumerate( form["inputs"].keys() ):
            form["inputs"][key]["bounds"] = target_function.bounds[:, i].tolist()

        ### adapt the objective to the target function
        for i, key in enumerate(form["obj"].keys()):
            form["obj"][key]["minimize"] = target_function.minimize

        return form


    def run_folder(self, function_name: str, seed: int) -> Path:
        """
        Folder where one optimization run is saved.
        """
        return (
            self.output_folder
            / self.name             # name of the benchmark
            / function_name         # name of the function
            / f"seed_{seed:04d}"    # name of the seed
        )


    def summary(self) -> str:
        """
        Summary of the configuration 
        used by the runner.
        """
        txt = []

        txt.append("=" * 60)
        txt.append("Benchmark configuration")
        txt.append("=" * 60)

        txt.append(f"Name            : {self.name}")
        txt.append(f"Functions       : {self.function_names}")
        txt.append(f"Seeds           : {self.seeds}")
        txt.append(f"Strategy        : {self.strategy_name}")
        txt.append(f"Acquisition     : {self.acquisition_name}")
        txt.append(f"Iterations      : {self.iterations}")
        txt.append(f"N_func          : {self.n_func}") 
        txt.append(f"N_runs          : {self.n_runs}")
        txt.append(f"Output folder   : {self.output_folder}")

        if self.notes:
            txt.append("")
            txt.append("Notes")
            txt.append("-----")
            txt.append(self.notes)

        return "\n".join(txt)