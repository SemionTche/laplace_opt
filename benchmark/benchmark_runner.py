from __future__ import annotations

from datetime import datetime
import pandas as pd

from laplace_log import log

from .benchmark_config import BenchmarkConfig
from .benchmark_experiment import BenchmarkExperiment
from .benchmark_result import BenchmarkResult


class BenchmarkRunner:

    def __init__(self, config: BenchmarkConfig):

        self.config = config

        self.results = []


    def run(self) -> list[BenchmarkResult]:

        log.info("")
        log.info("=" * 60)
        log.info("Starting benchmark run")
        log.info("=" * 60)
        log.info(self.config.summary())

        total_func = len(self.config.target_functions)
        total_seeds = len(self.config.seeds)

        for i, target_function in enumerate(self.config.target_functions):

            name_func = self.config.function_names[i]
            
            log.info("")
            log.info(f"[{i+1}/{total_func}] Func {name_func}")

            for j, seed in enumerate(self.config.seeds):

                log.info("")
                log.info(f"[{j+1}/{total_seeds}] Seed {seed} Func {name_func}")

                experiment = BenchmarkExperiment(
                    config=self.config,
                    target_function=target_function,
                    seed=seed,
                )

                result = experiment.run()

                save_folder = self.config.run_folder(
                    function_name=name_func, 
                    seed=seed
                )
                result.save(save_folder)

                self.results.append(result)

        log.info("")
        log.info("=" * 60)
        log.info("Benchmark completed")
        log.info("=" * 60)

        return self.results


    @property
    def dataframe(self) -> pd.DataFrame:

        rows = []

        for r in self.results:

            rows.append(
                {
                    "benchmark": r.benchmark_name,
                    "function": r.function_name,
                    "acquisition": r.acquisition,
                    "strategy": r.strategy,
                    "seed": r.seed,
                    "evaluations": r.n_evaluations,
                    "elapsed_time": r.elapsed_time,
                }
            )

        return pd.DataFrame(rows)


    def save_summary(self) -> None:

        if not self.results:
            return

        folder = (
            self.config.output_folder
            / self.config.name
        )

        folder.mkdir(parents=True, exist_ok=True)

        csv_path = folder / "summary.csv"

        self.dataframe.to_csv(
            csv_path,
            mode="a",
            header=not csv_path.exists(),
            index=False,
        )

        if self.config.notes:
            notes_path = folder / "notes.txt"

            with notes_path.open("a", encoding="utf-8") as f:
                f.write(f"=== {datetime.now():%Y-%m-%d %H:%M:%S} ===\n")
                f.write(self.config.notes)
                f.write("\n\n")

