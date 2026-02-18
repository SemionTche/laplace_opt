# libraries
from abc import ABC, abstractmethod

from botorch.models.model import Model

# project
from laplace_opt.core.optimizerContext import OptimizationContext


class StrategyStructure(ABC):
    '''
    Base class for model construction strategies.

    This class defines a common interface for building surrogate models
    used in Bayesian optimization. Subclasses should implement the
    `build_model` method to return a fitted BoTorch model.
    '''
    
    display_name: str
    description: str
    parameters: dict

    # parameters required for every strategy
    core_parameters = {
        "n_repeats": {
            "type": int,
            "default": 1,
            "min": 1,
            "max": 1000,
            "label": "Number sample repeats",
            "description": "Number of repeated evaluations per candidate."
        },

        "save_period": {
            "type": int,
            "default": 5,
            "min": 0,
            "max": 100,
            "label": "Saving period",
            "description": (
                "Number of optimization steps between automatic saves of observations and model state.\n"
                "Set to 0 to disable periodic saving."
            )
        },

        "seed": {
            "type": int,
            "default": 0,
            "min": 0,
            "max": 999_999,
            "label": "Seed",
            "description": "Seed for random generation"
        },

        "q_candidates": {
            "type": int,
            "default": 1,
            "min": 1,
            "max": 1024,
            "label": "Number of candidates",
            "description": "Number of candidates proposed in one optimization step"
        },

        "num_restarts": {
            "type": int,
            "default": 5,
            "min": 1,
            "label": "Number of restarts",
            "description": (
                "Number of multistart local optimizations used to maximize the acquisition function.\n"
                "Higher values improve robustness but increase computational cost.\n"
                "Must be < 'raw_samples' (to be sure that there is enough points to start from)"
            )
        },

        "raw_samples": {
            "type": int,
            "default": 10,
            "label": "Raw samples",
            "description": (
                "Number of Sobol samples used to initialize multistart optimization.\n"
                "Larger values improve restart quality but increase computational cost.\n"
                "Must be > 'num_restarts' (to be sure that there is enough points to start from)"
            )
        },

    }


    @abstractmethod
    def build_model(self,
                    context: OptimizationContext,
                    **params) -> Model:
        '''
        Construct and fit a surrogate model.

        Args:
            context: (OptimizationContext)
                Optimization context providing training inputs, observations,
                bounds, and objective structure required to build the model.

            **params:
                Additional keyword arguments defining model-specific
                hyperparameters (e.g., kernel type, output transforms).

        Returns:
            Model:
                A fitted BoTorch model representing the surrogate posterior,
                ready to be used by an acquisition function.
        '''

