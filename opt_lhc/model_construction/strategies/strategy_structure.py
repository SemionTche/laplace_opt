from abc import ABC, abstractmethod
import torch
from core.optimizerContext import OptimizationContext

class StrategyStructure(ABC):
    display_name: str
    description: str
    parameters: dict

    core_parameters = {
        "q_candidates": {
            "type": int,
            "default": 1,
            "min": 1,
            "max": 1024,
            "label": "Number of candidates",
            "description": "Number of proposal for each sample"
        },

        "num_restarts": {
            "type": int,
            "default": 8,
            "label": "Number of restarts",
            "description": ""
        },

        "raw_samples": {
            "type": int,
            "default": 10,
            "label": "Raw samples",
            "description": ""
        },

    }

    @abstractmethod
    def build_model(
        self,
        context: OptimizationContext,
        **params
    ):
        """Return a fitted BoTorch model"""

    # @abstractmethod
    # def get_default_sampler(self, model):
    #     """Return a sampler compatible with this model"""

