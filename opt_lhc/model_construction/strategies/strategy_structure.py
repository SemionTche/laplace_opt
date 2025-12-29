from abc import ABC, abstractmethod
import torch

class StrategyStructure(ABC):
    display_name: str
    description: str
    parameters: dict

    @abstractmethod
    def build_model(
        self,
        train_X: torch.Tensor,
        train_Y: torch.Tensor,
        bounds: torch.Tensor,
        **params
    ):
        """Return a fitted BoTorch model"""

    @abstractmethod
    def get_default_sampler(self, model):
        """Return a sampler compatible with this model"""

