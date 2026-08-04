from __future__ import annotations

from pathlib import Path

from ..benchmark_result import BenchmarkResult


class BenchmarkLoader:

    def __init__(self, root):

        self.root = Path(root)

    def load(self):

        results = []

        for file in self.root.rglob("benchmark_result.pt"):

            try:

                result = BenchmarkResult.load(file.parent)

                results.append(result)

            except Exception as e:

                print(f"Cannot load {file}: {e}")

        return results


    def load_function(self, function_name):

        return [

            r

            for r in self.load()

            if r.function_name == function_name

        ]


    def load_seed(self, seed):

        return [

            r

            for r in self.load()

            if r.seed == seed

        ]


    def load_strategy(self, strategy):

        return [

            r

            for r in self.load()

            if r.strategy == strategy

        ]


    def load_acquisition(self, acquisition):

        return [

            r

            for r in self.load()

            if r.acquisition == acquisition

        ]