import torch
from tests.test_function.target_function import target_function


def run_multi_objective(
    optimizer,
    n_iterations: int = 15,
):
    """
    Generic multi-objective optimization loop.

    Args:
        optimizer: Initialized Optimizer instance
        n_iterations: Number of optimization steps
    """
    for it in range(n_iterations):
        X = optimizer.get_candidates()   # [q, d]
        Y = target_function(X[:, 0], X[:, 1])  # [q, 2]

        optimizer.update_data(X, Y)

        ref = optimizer.context.compute_ref_point()

        print(
            f"[MO] Iter {it:02d} | "
            f"ref_point = {ref.tolist()}"
        )
