from abc import ABC, abstractmethod
import torch

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
    }

    @abstractmethod
    def build_model(
        self,
        train_X: torch.Tensor,
        train_Y: torch.Tensor,
        bounds: torch.Tensor,
        **params
    ):
        """Return a fitted BoTorch model"""

    # @abstractmethod
    # def get_default_sampler(self, model):
    #     """Return a sampler compatible with this model"""

