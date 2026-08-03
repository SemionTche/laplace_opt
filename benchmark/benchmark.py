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

from .functions import Ackley, Booth
# ---------------------------------------------------------


# logs
LoggerLHC(
    "laplace.benchmark",
    file_level="info",
    console_level="warning",
)
log.info("Starting benchmark...")

logging.getLogger(LOGGER_NAME).setLevel(logging.INFO)
logging.getLogger("matplotlib").setLevel(logging.WARNING)



if __name__ == "__main__":

    cfg = BenchmarkConfig(
        name="PhysicsToy",
        optimizer_form=OPT_FORM_SINGLE,
        target_functions=[Booth(), Ackley()],
        iterations=10,
        seeds=list(range(5)),
        output_folder=Path("benchmark/results"),
        notes=""
    )

    runner = BenchmarkRunner(cfg)
    runner.run()
    runner.save_summary()