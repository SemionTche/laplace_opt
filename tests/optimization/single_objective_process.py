import torch
from tests.test_function.target_function import target_function


def run_single_objective(
    optimizer,
    n_iterations: int = 15,
):
    """
    Generic single-objective optimization loop.

    Args:
        optimizer: Initialized Optimizer instance
        n_iterations: Number of optimization steps
    """
    best_value = -float("inf")

    for it in range(n_iterations):
        # ask optimizer for candidates
        X = optimizer.get_candidates()      # shape [q, d]

        # evaluate objective
        Y_full = target_function(X[:, 0], X[:, 1])
        Y = Y_full[:, 0:1]                  # single objective

        # feed data back through optimizer API
        optimizer.update_data(X, Y)

        best_value = max(best_value, Y.max().item())

        print(
            f"[SO] Iter {it:02d} | "
            f"best = {best_value:.4f}"
        )

    return best_value
