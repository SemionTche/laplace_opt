from __future__ import annotations


import pandas as pd

from .benchmark_analysis import BenchmarkAnalysis


class BenchmarkTables:
    """
    Utilities to generate benchmark tables.
    """

    def __init__(self, analysis: BenchmarkAnalysis):

        self.analysis = analysis


    def runs(self):
        """
        One row per optimization run.
        """
        return (
            self.analysis.dataframe()
        )


    def comparison(self):
        """
        Mean/std comparison table.
        """
        df = self.runs()

        metrics = [

            "simple_regret",

            "auc_regret",

            "time_to_eps",

            "distance_x",

        ]

        table = (
            df.groupby(
                [
                    "function",
                    "strategy",
                    "acquisition"
                ]
            )[metrics]
            .agg(
                [
                    "mean",
                    "std"
                ]
            )
        )

        return table


    def ranking(self, metric="simple_regret"):
        """
        Rank strategies.

        Lower is better.
        """
        df = self.runs()

        ranking = (
            df
            .groupby(
                [
                    "strategy",
                    "acquisition"
                ]
            )[metric]
            .mean()
            .sort_values()
        )

        return ranking


    def formatted(self, metric="simple_regret"):

        df = self.runs()

        table = (
            df
            .groupby(
                [
                    "strategy",
                    "acquisition"
                ]
            )[metric]
            .agg(
                [
                    "mean",
                    "std"
                ]
            )
        )

        table["result"] = (
            table["mean"]
            .map(
                lambda x:
                f"{x:.3e}"
            )
            +
            " ± "
            +
            table["std"]
            .map(
                lambda x:
                f"{x:.3e}"
            )
        )

        return table[
            ["result"]
        ]


    def to_csv(self, path):

        self.comparison().to_csv(
            path
        )


    def to_latex(self, path):

        latex = (
            self.comparison()
            .to_latex()
        )

        with open(
            path,
            "w"
        ) as f:

            f.write(latex)





   # table, ax = plt.subplots(1, 1, figsize=(18, 18))
    # ax = make_df(ax=ax, df=self.df)


    # def make_df(self, ax: Axes, df):
    #     """
    #     Display a pandas DataFrame as a matplotlib table.

    #         Args:
    #             ax (Axes):
    #                 Axis on which to draw the table.
                
    #             df (DataFrame, optional):
    #                 DataFrame to display. If None, uses self.df.
    #     """
    #     if df is None:
    #         df = self.df

    #     ax.clear()
    #     ax.axis("off")

    #     # Round floats for readability
    #     display_df = df.copy()
    #     display_df = display_df.round(3)

    #     table = ax.table(
    #         cellText=display_df.values,
    #         rowLabels=display_df.index.astype(str),
    #         colLabels=display_df.columns.astype(str),
    #         loc="center",
    #         cellLoc="center",
    #     )

    #     table.auto_set_font_size(False)
    #     table.set_fontsize(7)
    #     table.scale(1.2, 1.4)

    #     # Optional styling
    #     for (row, col), cell in table.get_celld().items():
    #         if row == 0:  # header
    #             cell.set_text_props(weight="bold")
    #             cell.set_facecolor("#DDDDDD")
    #         if col == -1:  # index column
    #             cell.set_text_props(weight="bold")
    #             cell.set_facecolor("#F5F5F5")

    #     return table
