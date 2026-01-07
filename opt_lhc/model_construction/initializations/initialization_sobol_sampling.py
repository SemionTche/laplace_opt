# libraries
from botorch.utils.sampling import draw_sobol_samples

# project
from model_construction.initializations.initialization_structure import InitializationStructure


class SobolInitialization(InitializationStructure):
    display_name = "Sobol Sampling"
    description = "Low-discrepancy Sobol sequence initialization"

    parameters = {
        "n_samples": {
            "type": int,
            "default": 16,
            "min": 1,
            "max": 1024,
            "label": "Number of samples",
            "description": "Number of points to sample"
        },
        "q_candidates": {
            "type": int,
            "default": 1,
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

    def generate(bounds, n_samples: int = 16, q_candidates: int = 1, seed: int = 0):
        # bounds: Tensor [2, d]
        X = draw_sobol_samples(
            bounds=bounds,
            n=n_samples,
            q=q_candidates,
            seed=seed
        ).squeeze(1)
        return X
