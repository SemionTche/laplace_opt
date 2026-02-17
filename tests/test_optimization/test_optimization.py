# libraries
from typing import Callable

from laplace_log import log

# project
from laplace_opt.core.optimizer import Optimizer

# tests
from .dummy_server_response import dummy_server_results
from .plot_results import (
    plot_single_objective_summary, plot_multi_objective_summary
)


def test_optimization(optimizer: Optimizer, 
                      target_function: Callable, 
                      n_iterations: int, 
                      mode: str) -> None:
    '''
    Run a synchronous multi-objective optimization loop for testing.

    At each iteration, candidates proposed by the optimizer are evaluated
    using a dummy server and fed back to the optimizer.
    '''
    log.info("Testing optimization...")
    log.info(f"Test mode: {mode}")
    last_payload = None                     # holder to get the candidates

    def capture(payload):                   # function made to catch the signal of new candidates
        nonlocal last_payload
        last_payload = payload

    # connect the new candidates to the capture
    optimizer.new_candidates.connect(capture)

    # generate the initialization
    n_init = 0
    optimizer.init_opt()
    if last_payload:
        n_init = len(last_payload["samples"])  # the first payload is the initialization batch

    for it in range(n_iterations):  # for each step
        if last_payload is None:    # if no data got catched
            raise RuntimeError("No candidates received")  # raise an error

        # generate the dummy server response (evaluating the target function)
        server_reply = dummy_server_results(last_payload, target_function)

        optimizer.update_opt(server_reply)  # update the server

    # at the end, plot the optimization result
    if mode == "single":
        plot_single_objective_summary(optimizer, target_function, n_init)
    
    elif mode == "multi":
        plot_multi_objective_summary(optimizer, target_function, n_init)
