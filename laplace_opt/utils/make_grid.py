import torch

from botorch.utils.sampling import draw_sobol_samples


def make_grid(bounds, n_per_dim=100):
    '''Return in physical space'''
    d = bounds.shape[1]

    if d <= 2:

        axes = [
            torch.linspace(bounds[0, i], bounds[1, i], n_per_dim)
            for i in range(d)
        ]

        mesh = torch.meshgrid(*axes, indexing="ij")

        X = torch.stack(
            [m.reshape(-1) for m in mesh],
            dim=-1,
        )
    
    else:
        X = draw_sobol_samples(
            bounds=bounds,
            n=n_per_dim,
            q=1,
        ).squeeze(1)


    return X