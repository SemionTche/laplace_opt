from botorch.utils.sampling import draw_sobol_samples

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
            "label": "Number of samples"
        }
    }

    def generate(self, bounds, n_samples: int = 16):
        # bounds: Tensor [2, d]
        X = draw_sobol_samples(
            bounds=bounds,
            n=n_samples,
            q=1
        ).squeeze(1)
        return X
