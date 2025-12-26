# core/optManager.py
from typing import Optional
import torch

from core.optimizer import Optimizer


class OptManager:
    def __init__(self):
        self.optimizer: Optional[Optimizer] = None
        self.model_config = None
        self.bounds = None

        self.train_X = None
        self.train_Y = None

    # ---------- configuration ----------
    def configure_model(self, model_config: dict, bounds: torch.Tensor):
        """
        Called once when user presses Start.
        """
        self.model_config = model_config
        self.bounds = bounds

        if not model_config["enabled"]:
            self.optimizer = None
            return

        self.optimizer = Optimizer(
            bounds=bounds,
            classes=model_config["classes"],
            hyperparameters=model_config["hyperparameters"],
        )

    # ---------- initialization ----------
    def initialize(self, X_init: torch.Tensor, Y_init: Optional[torch.Tensor] = None):
        self.train_X = X_init
        self.train_Y = Y_init

        if self.optimizer is not None and Y_init is not None:
            self.optimizer.initialize(X_init, Y_init)

    # ---------- data updates ----------
    def add_data(self, X_new: torch.Tensor, Y_new: torch.Tensor):
        self.train_X = torch.cat([self.train_X, X_new], dim=0)
        self.train_Y = torch.cat([self.train_Y, Y_new], dim=0)

        if self.optimizer is not None:
            self.optimizer.update_data(X_new, Y_new)

    # ---------- optimization ----------
    def get_next_candidates(self, q: int):
        if self.optimizer is None:
            raise RuntimeError("Optimizer not enabled")

        return self.optimizer.get_next_candidates(q)
