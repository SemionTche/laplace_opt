"""
Main benchmark launcher.
"""

from pathlib import Path
import logging

from laplace_log import LoggerLHC, log
from laplace_server.protocol import LOGGER_NAME

from .benchmark_runner import BenchmarkRunner
from .benchmark_config import BenchmarkConfig


### select the benchmark parameters
# ---------------------------------------------------------
from .starter.opt_form_single import OPT_FORM_SINGLE
from .starter.opt_form_multi import OPT_FORM_MULTI

from .functions import Ackley, Booth, Sphere
# ---------------------------------------------------------


# logs
LoggerLHC(
    "laplace.benchmark",
    file_level="info",
    console_level="warning",
)

logging.getLogger(LOGGER_NAME).setLevel(logging.INFO)
logging.getLogger("matplotlib").setLevel(logging.WARNING)



if __name__ == "__main__":

    cfg = BenchmarkConfig(
        name="bench_test_1",
        optimizer_form=OPT_FORM_SINGLE,
        target_functions=[Ackley(), Booth(), Sphere()],
        iterations=30,
        seeds=list(range(5)),
        output_folder=Path("benchmark/results"),
        notes="Test"
    )

    runner = BenchmarkRunner(cfg)
    runner.run()
    runner.save_summary()