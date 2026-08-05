from dataclasses import dataclass

import torch
from botorch.models.model import Model


@dataclass(slots=True)
class ModelSnapshot:

    iteration: int

    model: Model

    train_X: torch.Tensor

    train_Y: torch.Tensor


    def copy(self):

        return ModelSnapshot(

            iteration=self.iteration,

            model=self.model,

            train_X=self.train_X.clone(),

            train_Y=self.train_Y.clone(),

        )