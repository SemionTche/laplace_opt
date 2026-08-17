from __future__ import annotations

from pathlib import Path
from collections import defaultdict
import gc

import numpy as np
import pandas as pd

from .analysis_record import AnalysisRecord
from .benchmark_analyzer import BenchmarkAnalyzer
from .benchmark_loader import BenchmarkLoader

from ..metrics import METRICS
from ..bench_utils.normalize import norm_curve


class BenchmarkAnalysis:
    """
    Analysis of a complete benchmark campaign.
    """

    def __init__(self, loader: BenchmarkLoader):
        """
        Args:
            loader (BenchmarkLoader):
                Object from which extract the data.
                Either using a load or an iterative method.
        """
        self.records: list[AnalysisRecord] = []
        self.curve_names = [
            # "best_curve",
            "regret_curve",
            # "cumulative_regret_curve",
            # "regret_instantaneous",
            "noise_curve",
            "contraction_variance_curve",
            "contraction_entropy_curve",

            # "lengthscale_curve",
            # "contraction_variance_rate",
        ]
        
        self._process(loader)

        self.df = self.dataframe()
        self.agg = self.aggregate()

        print("Analysis generated.")


    def dataframe(self) -> pd.DataFrame:
        """Full analysis dataframe."""
        rows = []

        for r in self.records:
            rows.append(r.summary())

        return pd.DataFrame(rows)


    def aggregate(self,
                  group_by=[
                      "function",
                      "strategy",
                      "acquisition",]) -> pd.DataFrame:
        """
        Aggregate the relevant features.

        Computes:
            mean and std
        """
        metrics = []
        for metric in METRICS.values():
            metrics.append(metric.name)
            if metric.relative_name is not None:
                metrics.append(metric.relative_name)

        grouped = (
            self.df.groupby(group_by)[metrics].agg(
                [
                    "mean",
                    "std",
                ]
            )
        )
        return grouped



    def _process(self, loader: BenchmarkLoader):
        for result in loader.iter_load():
            analyzer = BenchmarkAnalyzer(result=result)
            record = analyzer.to_record()

            self.records.append(record)

        del analyzer
        del result
        gc.collect()




    def curves(self,
               curve: str,
               *,
               normalization: str | None = None,
               reduction: str | None = None,
               groupby=("function",),):
        """
        Parameters
        ----------
        curve : str
            Name of the BenchmarkAnalyzer method.

        normalization
            None
            "relative"

        reduction
            None
            "mean"

        groupby
            Metadata used when averaging.
        """
        if curve not in self.curve_names:
            raise ValueError(
                f"Unknown curve '{curve}'. "
                f"Available curves: {self.curve_names}"
            )

        rows = []

        for record in self.records:

            values = record.curves[curve]
            # values = getattr(analyzer, curve)()

            values = norm_curve(
                curve=values,
                normalization=normalization,
            )

            # rows.append(
            #     {
            #         "function": analyzer.result.function_name,
            #         "strategy": analyzer.result.strategy,
            #         "acquisition": analyzer.result.acquisition,
            #         "seed": analyzer.result.seed,
            #         "curve": values,
            #     }
            # )

            rows.append(
                {
                    "function": record.function,
                    "strategy": record.strategy,
                    "acquisition": record.acquisition,
                    "seed": record.seed,
                    "curve": values,
                }
            )

        if reduction is None:
            return rows

        if reduction != "mean":
            raise ValueError(f"Unknown reduction '{reduction}'")

        groups = defaultdict(list)

        for row in rows:
            key = tuple(row[k] for k in groupby)
            groups[key].append(row["curve"])

        output = []

        for key, curves in groups.items():

            d = dict(zip(groupby, key))
            d["curve"] = np.mean(np.stack(curves), axis=0)

            output.append(d)

        return output


    def save_summary(self, path: Path) -> None:
        """Save the full analysis summary."""
        self.df.to_csv(path.with_suffix(".csv"), index=False)
        self.df.to_html(path.with_suffix(".htlm"))
        print("DataFrame saved.")


    def save_aggregate(self, path: Path) -> None:
        """Save the full analysis aggregate."""
        self.agg.to_csv(path.with_suffix(".csv"))
        self.agg.to_html(path.with_suffix(".htlm"))
        print("Aggregate saved.")