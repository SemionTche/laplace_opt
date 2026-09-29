from __future__ import annotations

from pathlib import Path

from ..experiment import BenchmarkResult


class BenchmarkLoader:
    """
    Helper loading all the BenchmarkResult from
    a benchmarker folder according to the relevant filer.
    """

    def __init__(self, root):
        self.root = Path(root)


    def load(self) -> list[BenchmarkResult]:

        results = []

        for file in self.root.rglob("benchmark_result.pt"):

            try:

                result = BenchmarkResult.load(file.parent)

                results.append(result)

            except Exception as e:

                print(f"Cannot load {file}: {e}")

        print(f"Benchark loaded from {self.root}.")
        return results


    def load_function(self, function_name: str) -> list[BenchmarkResult]:

        return [

            r

            for r in self.load()

            if r.function_name == function_name

        ]


    def load_seed(self, seed: int) -> list[BenchmarkResult]:

        return [

            r

            for r in self.load()

            if r.seed == seed

        ]


    def load_strategy(self, strategy: str) -> list[BenchmarkResult]:

        return [

            r

            for r in self.load()

            if r.strategy == strategy

        ]


    def load_acquisition(self, acquisition: str) -> list[BenchmarkResult]:

        return [

            r

            for r in self.load()

            if r.acquisition == acquisition

        ]


    def iter_paths(self):
        return list(
            self.root.rglob("benchmark_result.pt")
        )


    def iter_load(self):
        """
        Load one BenchmarkResult at a time.

        Only one result is yielded at a time.
        """

        files = list(
            self.root.rglob("benchmark_result.pt")
        )

        total = len(files)

        print(
            f"Found {total} benchmark results."
        )

        for i, file in enumerate(files, start=1):

            print(
                f"Loading result {i}/{total}: "
                f"{file.parent}"
            )

            try:

                result = BenchmarkResult.load(
                    file.parent
                )

                yield result

            except Exception as e:

                print(
                    f"Cannot load {file}: {e}"
                )