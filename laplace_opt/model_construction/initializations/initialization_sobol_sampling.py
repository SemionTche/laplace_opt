# libraries
from botorch.utils.sampling import draw_sobol_samples
import torch

# project
from laplace_opt.model_construction import InitializationStructure


class SobolInitialization(InitializationStructure):
    '''
    Initialization strategy based on Sobol low-discrepancy sampling.

    This class generates an initial design using a Sobol sequence,
    providing a space-filling and deterministic sampling of the
    optimization domain. It defines configurable parameters such
    as the number of samples, number of candidates per sample,
    and the random seed.
    '''
    display_name = "Sobol Sampling"
    description = "Low-discrepancy Sobol sequence initialization"

    parameters = {
        "n_samples": {
            "type": int,
            "default": 3,
            "min": 1,
            "max": 1024,
            "label": "Number of samples",
            "description": "Number of points to sample"
        },
        
        "q_candidates": {
            "type": int,
            "default": 2,
            "min": 1,
            "max": 1024,
            "label": "Number of candidates",
            "description": "Number of proposal for each sample"
        },
        
        "seed": {
            "type": int,
            "default": 0,
            "min": 0,
            "max": 999_999,
            "label": "Seed",
            "description": "Seed for random generation"
        }
    }

    def generate(self, 
                 bounds: torch.Tensor, 
                 n_samples: int=16, 
                 q_candidates: int=1, 
                 seed: int=0) -> tuple[torch.Tensor, None]:
        '''
        Generate an initial set of samples using Sobol sampling.

        Args:
            bounds: (torch.Tensor)
                Tensor of shape [2, d] defining lower and upper bounds
                of the search space.
            
            n_samples: (int)
                Number of Sobol samples to generate.
            
            q_candidates: (int)
                Number of candidates per sample (q-batch size).
            
            seed: (int)
                Seed for Sobol sequence generation.

        Returns:
            tuple[torch.Tensor, None]:
                A tuple where the first element is a tensor of shape
                [n_samples, q_candidates, d] containing the sampled
                points in physical space, and the second element is None.
        '''
        X_physical = draw_sobol_samples(
            bounds=bounds,
            n=n_samples,
            q=q_candidates,
            seed=seed
        )

        return (X_physical, None)
