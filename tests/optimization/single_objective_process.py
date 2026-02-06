# libraries
import torch
import matplotlib.pyplot as plt

from laplace_log import log

# tests
from ..dummy_server.dummy_server_response import dummy_server_results


def run_single_objective(optimizer, target_function, n_iterations: int = 15):
    '''
    Generic single-objective optimization loop.

    Args:
        optimizer: Initialized Optimizer instance
        n_iterations: Number of optimization steps
    '''
    log.info("Single objective test...")
    
    last_payload = None                     # get the candidates

    def capture(payload):                   # function made to catch the signal of new candidates
        nonlocal last_payload
        last_payload = payload
    
    # connect the new candidates to the capture
    optimizer.new_candidates.connect(capture)

    # generate the initialization
    optimizer.init_opt()
    n_init = len(last_payload["samples"])  # the first payload is the initialization batch

    for it in range(n_iterations):
        if last_payload is None:    # if no data got catched
            raise RuntimeError("No candidates received")  # raise an error
        
        server_reply = dummy_server_results(last_payload, target_function) # otherwise get the results

        optimizer.update_opt(server_reply)  # update the server
    
    plot_single_objective_summary(optimizer=optimizer, target_function=target_function, n_init=n_init)



def plot_single_objective_summary(optimizer, 
                                  target_function, 
                                  n_init: int, 
                                  n_grid: int = 50,
                                  cmap="viridis"):
    
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))

    # --- Gather sampled data ---
    all_points = torch.stack([obs.x for obs in optimizer.context._observations])
    all_values = torch.stack([y for y in optimizer.context.Y_physical])
    init_points = all_points[:n_init]
    bo_points   = all_points[n_init:]

    # --- Grid for imshow ---
    x1 = torch.linspace(optimizer.bounds[0, 0], optimizer.bounds[1, 0], n_grid)
    x2 = torch.linspace(optimizer.bounds[0, 1], optimizer.bounds[1, 1], n_grid)
    X1, X2 = torch.meshgrid(x1, x2, indexing="ij")

    Z1 = torch.zeros_like(X1)

    for i in range(n_grid):
        for j in range(n_grid):
            y = target_function(X1[i, j], X2[i, j])
            Z1[i, j] = y[0, 0]
    
    # === Left panel: Objective ===
    im0 = axs[0].imshow(
        Z1.T.numpy(),
        origin="lower",
        extent=(x1[0], x1[-1], x2[0], x2[-1]),
        aspect="auto",
        cmap=cmap,
    )
    fig.colorbar(im0, ax=axs[0], label="Objective")

            ### init
    for idx, pt in enumerate(init_points):
        axs[0].scatter(
            pt[0].item(), pt[1].item(),
            color="tab:green", marker="o", ec="k", s=50, zorder=3
        )
        axs[0].annotate(
            str(idx),
            (pt[0].item(), pt[1].item()),
            textcoords="offset points", xytext=(5, 5),
            ha="center", fontsize=10
        )
    
        ### bo
    for idx, pt in enumerate(bo_points, start=n_init):
        axs[0].scatter(
            pt[0].item(), pt[1].item(),
            color="tab:orange", marker="o", ec="k", s=40, zorder=3
        )
        axs[0].annotate(
            str(idx),
            (pt[0].item(), pt[1].item()),
            textcoords="offset points", xytext=(5, 5),
            ha="center", fontsize=10
        )

    axs[0].set_title("Objective")
    axs[0].set_xlabel("X1")
    axs[0].set_ylabel("X2")


    # === Right panel: Objective along iteration ===
    
    axs[1].scatter(
        range(all_values.shape[0]), 
        all_values, 
        marker="o", 
        c="tab:blue", 
        ec="k"
    )

    axs[1].set_title("Objective evolution accross iterations")
    axs[1].set_xlabel("Number of iteration")
    axs[1].set_ylabel("Objective")
    
    plt.show()
    