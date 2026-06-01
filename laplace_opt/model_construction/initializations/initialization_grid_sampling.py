# libraries
import torch

# project
from laplace_opt.model_construction import InitializationStructure


class GridInitialization(InitializationStructure):
    '''
    Initialization strategy making a grid sampling.
    '''
    display_name = "Grid Sampling"
    description = "Drawing a grid in the input space"

    parameters = {
        "n_per_dim": {
            "type": int,
            "default": 5,
            "min": 1,
            "max": 8000,
            "label": "Number of samples per dimension",
            "description": "Number of points per dimension"
        },
        
    }

    def generate(self, 
                 bounds: torch.Tensor, 
                 n_per_dim: int) -> tuple[torch.Tensor, None]:
        '''
        Generate an initial set of samples by making a regular grid.

        Args:
            bounds: (torch.Tensor)
                Tensor of shape [2, d] defining lower and upper bounds
                of the search space.
            
            n_per_dim: (int)
                Number of samples along each dimension.

        Returns:
            tuple[torch.Tensor, None]:
                A tuple where the first element is a tensor of shape
                [n_per_dim^d, d] containing the sampled points in 
                physical space, and the second element is None.
        '''
        d = bounds.shape[-1]

        axes = [
            torch.linspace(bounds[0, i], bounds[1, i], n_per_dim)
            for i in range(d)
        ]

        mesh = torch.meshgrid(*axes, indexing="ij")
        
        X_physical = torch.stack([m.reshape(-1) for m in mesh], dim=-1)
        
        X_physical = X_physical.unsqueeze(-2)  # (N, 1, d)
        
        return (X_physical, None)
