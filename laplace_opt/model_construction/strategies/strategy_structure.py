# libraries
from abc import ABC, abstractmethod

# project
from laplace_opt.core.optimizerContext import OptimizationContext

class StrategyStructure(ABC):
    display_name: str
    description: str
    parameters: dict

    # parameters required for every strategy
    core_parameters = {
        "number_shot": {
            "type": int,
            "default": 1,
            "min": 1,
            "max": 1000,
            "label": "Number of shots per sample",
            "description": "Indicate how many shots should be made for each sample"
        },

        "save_period": {
            "type": int,
            "default": 5,
            "min": 0,
            "max": 100,
            "label": "Saving period",
            "description": "Indicate the number of step before saving the observations and model"
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
            "description": "Number of multistart local optimizations used to maximize the acquisition function. Higher values improve robustness but increase cost."
        },

        "raw_samples": {
            "type": int,
            "default": 10,
            "label": "Raw samples",
            "description": (
                "Number of Sobol samples used to score the acquisition function and select starting points for the gradient optimization.\n"
                "Larger values improve 'restart' quality but increase cost."
            )

        },

    }

    @abstractmethod
    def build_model(self, context: OptimizationContext, **params):
        '''Return a fitted BoTorch model'''

