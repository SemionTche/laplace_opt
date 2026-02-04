# libraries
import torch
import matplotlib.pyplot as plt

from laplace_log import log

# tests
from ..dummy_server.dummy_server_response import dummy_server_results


# def pareto_front(Y: torch.Tensor) -> torch.Tensor:
#     '''
#     Compute the Pareto front assuming ALL objectives are maximized.

#     Args:
#         Y: Tensor of shape [n_points, 2]

#     Returns:
#         Tensor of Pareto-optimal points, shape [n_pareto, 2]
#     '''
#     if Y.numel() == 0:
#         return Y

#     if Y.shape[1] != 2:
#         raise ValueError("pareto_front currently supports exactly 2 objectives.")

#     # Sort by objective 0 (descending = best first)
#     order = torch.argsort(Y[:, 0], descending=True)
#     Y_sorted = Y[order]

#     pareto_mask = torch.zeros(Y_sorted.shape[0], dtype=torch.bool)

#     best_y2 = -torch.inf
#     for i in range(Y_sorted.shape[0]):
#         y2 = Y_sorted[i, 1]
#         if y2 > best_y2:
#             pareto_mask[i] = True
#             best_y2 = y2

#     return Y_sorted[pareto_mask]



def run_multi_objective(optimizer, 
                        target_function, 
                        n_iterations: int):
    '''
    Run a synchronous multi-objective optimization loop for testing.

    At each iteration, candidates proposed by the optimizer are evaluated
    using a dummy server and fed back to the optimizer.
    '''
    log.info("Multi objective test...")
    last_payload = None                     # get the candidates

    def capture(payload):                   # function made to catch the signal of new candidates
        nonlocal last_payload
        last_payload = payload

    # connect the new candidates to the capture
    optimizer.new_candidates.connect(capture)

    # generate the initialization
    optimizer.init_opt()
    n_init = len(last_payload["samples"])  # the first payload is the initialization batch

    pareto_history = []  # list of tensors: pareto front after each iteration

    for it in range(n_iterations):  # for each step
        if last_payload is None:    # if no data got catched
            raise RuntimeError("No candidates received")  # raise an error

        server_reply = dummy_server_results(last_payload, target_function) # otherwise get the results

        optimizer.update_opt(server_reply)  # update the server

        ref = optimizer.context.compute_ref_point()  # compute the ref point (worse than every sampled one)
        log.info(f"[Multi Obj] Iter {it:02d} | ref_point = {ref.tolist()}")  # add it in the log


        # compute Pareto front from all observed points
        Y = torch.stack([obs.y for obs in optimizer.context._observations])
        minimize_flags = [obj.minimize for obj in optimizer.context.objectives.values()]
        front = optimizer.context.get_pareto_front_physical()#, minimize_flags)

        # compare with previous front (skip first iteration)
    #     if pareto_history:
    #         prev_front = pareto_history[-1]
    #         # check if any new point extends the front
    #         new_points = []
    #         for y in front:
    #             if not any(torch.allclose(y, py) for py in prev_front):
    #                 new_points.append(y)
    #         log.debug(f"Iteration {it:02d} | {len(new_points)} new points extended the Pareto front")
    #     else:
    #         log.debug(f"Iteration {it:02d} | Pareto front initialized with {front.shape[0]} points")

    #     pareto_history.append(front)

    # log.debug(f"Pareto history: {pareto_history}")
    
    # # final summary
    # log.info("=== Multi-objective optimization summary ===")
    # for i, front in enumerate(pareto_history):
    #     log.info(f"Iter {i:02d} | Pareto front size: {front.shape[0]} points")

    plot_multi_objective_summary(optimizer, target_function, n_init)



def plot_multi_objective_summary(optimizer,
                                 target_function,
                                 n_init: int,
                                 n_grid: int = 50,
                                 cmap="viridis"):
    '''
    Plot a 3-panel summary of the multi-objective optimization:
      - Left: Objective 1 landscape + sampled points (annotated by order)
      - Middle: Final Pareto front in objective space + ref point
      - Right: Objective 2 landscape + sampled points (annotated by order)
    '''

    fig, axs = plt.subplots(1, 3, figsize=(18, 6))

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
    Z2 = torch.zeros_like(X2)

    for i in range(n_grid):
        for j in range(n_grid):
            y = target_function(X1[i, j], X2[i, j])
            Z1[i, j] = y[0, 0]
            Z2[i, j] = y[0, 1]

    # === Left panel: Objective 1 ===
    im0 = axs[0].imshow(
        Z1.T.numpy(),
        origin="lower",
        extent=(x1[0], x1[-1], x2[0], x2[-1]),
        aspect="auto",
        cmap=cmap,
    )
    fig.colorbar(im0, ax=axs[0], label="Objective 1")

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

    axs[0].set_title("Objective 1")
    axs[0].set_xlabel("X1")
    axs[0].set_ylabel("X2")

    # === Middle panel: Pareto front ===
    final_front = optimizer.context.get_pareto_front_physical()#, minimize_flags)

        ### init
    for idx in range(n_init):
        axs[1].scatter(
            all_values[idx, 0].item(),
            all_values[idx, 1].item(),
            color="tab:green", s=30, ec="k"
        )
        axs[1].annotate(
            str(idx),
            (all_values[idx, 0].item(), all_values[idx, 1].item()),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=9,
        )

        ### bo
    for idx in range(n_init, all_values.shape[0]):
        axs[1].scatter(
            all_values[idx, 0].item(),
            all_values[idx, 1].item(),
            color="tab:blue", s=30, ec="k"
        )
        axs[1].annotate(
            str(idx),
            (all_values[idx, 0].item(), all_values[idx, 1].item()),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=9,
        )

    if final_front.numel() > 0:
        axs[1].step(
            final_front[:, 0],
            final_front[:, 1],
            where="post",
            lw=2,
            color="tab:blue",
            zorder=3,
        )

        axs[1].scatter(
            final_front[:, 0],
            final_front[:, 1],
            color="tab:blue", s=150, ec="k", marker="^"
        )
        
        ### ref point
    ref = optimizer.context.compute_ref_point_physical()

    axs[1].scatter(ref[0], ref[1], color="red", ec="k", zorder=4)
    axs[1].annotate("ref", (ref[0], ref[1]), xytext=(5, 5), textcoords="offset points")

    axs[1].set_title("Final Pareto Front")
    axs[1].set_xlabel("Objective 1")
    axs[1].set_ylabel("Objective 2")

    # === Right panel: Objective 2 ===
    im2 = axs[2].imshow(
        Z2.T.numpy(),
        origin="lower",
        extent=(x1[0], x1[-1], x2[0], x2[-1]),
        aspect="auto",
        cmap="viridis",
    )
    fig.colorbar(im2, ax=axs[2], label="Objective 2")

        ### init
    for idx, pt in enumerate(init_points):
        axs[2].scatter(
            pt[0].item(), pt[1].item(),
            color="tab:green", marker="o", ec="k", s=50, zorder=3
        )
        axs[2].annotate(
            str(idx),
            (pt[0].item(), pt[1].item()),
            textcoords="offset points", xytext=(5, 5),
            ha="center", fontsize=10
        )
    
        ### bo
    for idx, pt in enumerate(bo_points, start=n_init):
        axs[2].scatter(
            pt[0].item(), pt[1].item(),
            color="tab:orange", marker="o", ec="k", s=40, zorder=3
        )
        axs[2].annotate(
            str(idx),
            (pt[0].item(), pt[1].item()),
            textcoords="offset points", xytext=(5, 5),
            ha="center", fontsize=10
        )

    axs[2].set_title("Objective 2")
    axs[2].set_xlabel("X1")
    axs[2].set_ylabel("X2")

    fig.tight_layout()
    plt.show()
