# libraries
import matplotlib.pyplot as plt
from typing import Callable

import torch
from laplace_log import log

# project
from laplace_opt.core.optimizer import Optimizer

# tests
from ..dummy_server.dummy_server_response import dummy_server_results


def run_multi_objective(optimizer: Optimizer, 
                        target_function: Callable, 
                        n_iterations: int) -> None:
    '''
    Run a synchronous multi-objective optimization loop for testing.

    At each iteration, candidates proposed by the optimizer are evaluated
    using a dummy server and fed back to the optimizer.
    '''
    log.info("Multi objective test...")
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
    plot_multi_objective_summary(optimizer, target_function, n_init)


def plot_multi_objective_summary(optimizer: Optimizer,
                                 target_function: Callable,
                                 n_init: int,
                                 n_grid: int = 50,
                                 cmap="viridis") -> None:
    '''
    Plot a 3-panel summary of the multi-objective optimization:
      - Left: Objective 1 landscape + sampled points (annotated by order)
      - Middle: Final Pareto front in objective space + ref point
      - Right: Objective 2 landscape + sampled points (annotated by order)
    '''

    fig, axs = plt.subplots(1, 3, figsize=(18, 6))

    ### Gather sampled data
    all_points = torch.stack([obs.x for obs in optimizer.context._observations])
    all_values = torch.stack([y for y in optimizer.context.Y_physical])
    init_points = all_points[:n_init]
    bo_points   = all_points[n_init:]

    ### Grid for imshow
    x1 = torch.linspace(optimizer.bounds[0, 0], optimizer.bounds[1, 0], n_grid)
    x2 = torch.linspace(optimizer.bounds[0, 1], optimizer.bounds[1, 1], n_grid)
    X1, X2 = torch.meshgrid(x1, x2, indexing="ij")

    Z1 = torch.zeros_like(X1)
    Z2 = torch.zeros_like(X2)

    for i in range(n_grid):
        for j in range(n_grid):
            y = target_function(X1[i, j], X2[i, j])
            Z1[i, j] = y[0, 0]
            Z2[i, j] = y[0, 1]


    ### Left panel: Objective 1

        # objective landscape
    im0 = axs[0].imshow(
        Z1.T.numpy(),
        origin="lower",
        extent=(x1[0], x1[-1], x2[0], x2[-1]),
        aspect="auto",
        cmap=cmap,
    )
    fig.colorbar(im0, ax=axs[0], label="Objective 1")

        # init
    for idx, pt in enumerate(init_points):          # for each initial position
        axs[0].scatter(                             # plot the position
            pt[0].item(), pt[1].item(),
            color="tab:green", marker="o", ec="k", s=50, zorder=3
        )
        axs[0].annotate(                            # annotate with the sampling index
            str(idx),
            (pt[0].item(), pt[1].item()),
            textcoords="offset points", xytext=(5, 5),
            ha="center", fontsize=10
        )
    
        # bo
    for idx, pt in enumerate(bo_points, start=n_init):      # for each optimization
        axs[0].scatter(                                     # plot the position
            pt[0].item(), pt[1].item(),
            color="tab:orange", marker="o", ec="k", s=50, zorder=3
        )
        axs[0].annotate(                                    # annotate with the sampling index
            str(idx),
            (pt[0].item(), pt[1].item()),
            textcoords="offset points", xytext=(5, 5),
            ha="center", fontsize=10
        )
        
        # labels
    axs[0].set_title("Objective 1")
    axs[0].set_xlabel("X1")
    axs[0].set_ylabel("X2")


    ### Middle panel: Pareto front
    final_front = optimizer.context.get_pareto_front_physical()  # compute the Pareto front
    ref = optimizer.context.compute_ref_point_physical()         # compute the reference point

        # init
    for idx in range(n_init):               # for each initial position
        axs[1].scatter(                     # plot the value
            all_values[idx, 0].item(),
            all_values[idx, 1].item(),
            color="tab:green", s=30, ec="k"
        )
        axs[1].annotate(                    # annotate with the sampling index
            str(idx),
            (all_values[idx, 0].item(), all_values[idx, 1].item()),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=9,
        )

        # bo
    for idx in range(n_init, all_values.shape[0]):      # for each optimization
        axs[1].scatter(                                 # plot the value
            all_values[idx, 0].item(),
            all_values[idx, 1].item(),
            color="tab:blue", s=30, ec="k"
        )
        axs[1].annotate(                                # annotate with the sampling index
            str(idx),
            (all_values[idx, 0].item(), all_values[idx, 1].item()),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=9,
        )

    if final_front.numel() > 0:                         # if a Pareto was found
        axs[1].step(                                    # print the Pareto line
            final_front[:, 0],
            final_front[:, 1],
            where="post",
            lw=2,
            color="tab:blue",
            zorder=3,
        )

        axs[1].scatter(                                 # plot bigger the Pareto front values
            final_front[:, 0],
            final_front[:, 1],
            color="tab:blue", s=100, ec="k", marker="^"
        )
        
        # ref point
    axs[1].scatter(ref[0], ref[1], color="red", ec="k", zorder=4)
    axs[1].annotate("ref", (ref[0], ref[1]), xytext=(5, 5), textcoords="offset points")

        # labels
    axs[1].set_title("Final Pareto Front")
    axs[1].set_xlabel("Objective 1")
    axs[1].set_ylabel("Objective 2")


    ### Right panel: Objective 2

        # objective landscape
    im2 = axs[2].imshow(
        Z2.T.numpy(),
        origin="lower",
        extent=(x1[0], x1[-1], x2[0], x2[-1]),
        aspect="auto",
        cmap="viridis",
    )
    fig.colorbar(im2, ax=axs[2], label="Objective 2")

        # init
    for idx, pt in enumerate(init_points):                      # for each initial position
        axs[2].scatter(                                         # plot the position
            pt[0].item(), pt[1].item(),
            color="tab:green", marker="o", ec="k", s=50, zorder=3
        )
        axs[2].annotate(                                        # annotate with the sampling index
            str(idx),
            (pt[0].item(), pt[1].item()),
            textcoords="offset points", xytext=(5, 5),
            ha="center", fontsize=10
        )
    
        # bo
    for idx, pt in enumerate(bo_points, start=n_init):          # for each optimization
        axs[2].scatter(                                         # plot the position
            pt[0].item(), pt[1].item(),
            color="tab:orange", marker="o", ec="k", s=50, zorder=3
        )
        axs[2].annotate(                                        # annotate with the sampling index
            str(idx),
            (pt[0].item(), pt[1].item()),
            textcoords="offset points", xytext=(5, 5),
            ha="center", fontsize=10
        )

        # labels
    axs[2].set_title("Objective 2")
    axs[2].set_xlabel("X1")
    axs[2].set_ylabel("X2")

    fig.tight_layout()
    plt.show()
