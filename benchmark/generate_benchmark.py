from pathlib import Path
import logging

from laplace_log import LoggerLHC, log
from laplace_server.protocol import LOGGER_NAME

from .experiment import BenchmarkRunner, BenchmarkConfig

### select the benchmark parameters
# ---------------------------------------------------------
from .starter.opt_form_single import OPT_FORM_SINGLE
from .starter.opt_form_multi import OPT_FORM_MULTI

from .functions import (
    # straightforward
    Booth, Sphere,

    # find the min
    Beale, Rosenbrock, StyblinskiTang,

    # don't get trap
    GoldsteinPrice, Rastrigin, Ackley,

    # decide the minimum
    BraninHoo, Himmelblau,

    # additional features (adding noise or maximizing)
    NoisyFunction, ReverseFunction
)
# ---------------------------------------------------------


# logs
LoggerLHC(
    "laplace.benchmark",
    file_level="info",
    console_level="info",
)

logging.getLogger(LOGGER_NAME).setLevel(logging.INFO)
logging.getLogger("matplotlib").setLevel(logging.WARNING)


if __name__ == "__main__":

    # run a benchmark
    
    cfg = BenchmarkConfig(
        name="bench_test_10",

        optimizer_form=OPT_FORM_SINGLE,

        target_functions=[
            Booth(), 
            Sphere(),
            # StyblinskiTang(),
            # Rosenbrock(),
            # Ackley(),
            # Himmelblau()
        ],

        iterations=3,

        seeds=list(range(2)),

        output_folder=Path("benchmark/results"),

        notes="Test 10 ; logs test"
    )

    runner = BenchmarkRunner(cfg)  # create the runner
    runner.run()                   # run it
    runner.save_summary()          # save runner summary