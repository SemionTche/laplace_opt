# libraries
import logging
from laplace_log import LoggerLHC, log

# project
from laplace_opt.core.optimizer import Optimizer
from laplace_opt.utils.json_encoder import json_style

# tests
from tests.convert_opt_form import convert_opt_form
from tests.test_optimization.test_optimization import run_test_optimization
from tests.test_function.target_function import target_function
from tests.form_to_test import OPT_FORM_MULTI, OPT_FORM_SINGLE


# Initialize the logger
LoggerLHC("laplace.opt.tests", file_level="info", console_level="info")
logging.getLogger("matplotlib").setLevel(logging.WARNING)
log.info("Starting Opt Tests...")


# ==========================
# USER CONFIGURATION
# ==========================
n_iterations = 30        # number of candidate generation (number of optimization steps)
OPT_FORM = OPT_FORM_MULTI


if __name__ == "__main__":

    OPT_FORM = convert_opt_form(OPT_FORM)  # convert the OPT_FORM made by the user in the version needed by the optimizer

    log.info(f"Opt form:\n" + json_style(OPT_FORM))  # print the OPT_FORM in logs

    optimizer = Optimizer(OPT_FORM)                  # create the optimizer

    if len(OPT_FORM["obj"]) > 1:                     # define the test mode (single of multi - objective)
        TEST_MODE = "multi"
    elif 1 >= len(OPT_FORM["obj"]) > 0:
        TEST_MODE = "single"
    else:
        TEST_MODE = "Unknown"


    run_test_optimization(
            optimizer,
            target_function=target_function,
            n_iterations=n_iterations,
            mode=TEST_MODE
    )
