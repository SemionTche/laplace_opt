from dataclasses import dataclass

from torch import Tensor
from botorch.models import ModelListGP


@dataclass(slots=True)
class ModelSnapshot:

    iteration: int

    model: ModelListGP

    train_X: Tensor

    train_Y: Tensor


    def copy(self):

        return ModelSnapshot(
            iteration=self.iteration,

            model=self.model,

            train_X=self.train_X.clone(),

            train_Y=self.train_Y.clone(),
        )