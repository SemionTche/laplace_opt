import torch

def target_function_2(x1, x2):
    """
    Objective that we want to optimize.
    
    Args:
        x1, x2: coordinates, can be scalars or batched tensors
    """
    result_1 = (
        torch.exp(-(x1 - 1) ** 2 - (x2 - 6) ** 2)
        + torch.exp(-(x1 - 3) ** 2 / 10 - (x2 - 4) ** 2 / 4)
        + 1 / (x1 ** 2 + x2 ** 2 + 2)
    )

    result_2 = (
        -torch.exp(-(x1 - 2) ** 2 - (x2 - 4) ** 2)
        + 1 / (x1 ** 4 + x2 ** 2 + 1)
        - torch.exp(-(x1 - 3) ** 2 / 8 - (x2 - 7) ** 2 / 6)
    )
    
    # Assurer que result_1 et result_2 sont au moins 1D
    result_1 = result_1.unsqueeze(0) if result_1.ndim == 0 else result_1
    result_2 = result_2.unsqueeze(0) if result_2.ndim == 0 else result_2
    
    # Maintenant on les empile et on transpose pour obtenir [N, 2]
    stacked = torch.stack([result_1, result_2], dim=-1)  # shape [N, 2]
    
    return stacked
