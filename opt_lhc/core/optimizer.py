# core/optimizer.py
import torch
from typing import Dict, Type

from botorch.models import SingleTaskGP, ModelListGP
from gpytorch.mlls import ExactMarginalLogLikelihood
from botorch import fit_gpytorch_mll
from botorch.optim import optimize_acqf
from botorch.utils.transforms import normalize, unnormalize


class Optimizer:
    def __init__(
        self,
        bounds: torch.Tensor,
        classes: Dict[str, Type],
        hyperparameters: Dict[Type, dict],
    ):
        self.bounds = bounds
        self.bounds_norm = normalize(bounds, bounds)

        self.model_cls = classes["model"]
        self.fitter_cls = classes["fitter"]
        self.acq_cls = classes["acquisition"]
        self.sampler_cls = classes["sampler"]

        self.params = hyperparameters

        self.train_X = None
        self.train_Y = None

    # ---------- data ----------
    def initialize(self, X: torch.Tensor, Y: torch.Tensor):
        self.train_X = X
        self.train_Y = Y

    def update_data(self, X_new: torch.Tensor, Y_new: torch.Tensor):
        self.train_X = torch.cat([self.train_X, X_new], dim=0)
        self.train_Y = torch.cat([self.train_Y, Y_new], dim=0)

    # ---------- optimization ----------
    def get_next_candidates(self, q: int):
        X_norm = normalize(self.train_X, self.bounds)

        models = []
        for i in range(self.train_Y.shape[-1]):
            gp = self.model_cls()
            gp.build(
                X_norm,
                self.train_Y[:, i : i + 1],
                **self.params.get(self.model_cls, {})
            )

            mll = ExactMarginalLogLikelihood(gp.likelihood, gp)
            fit_gpytorch_mll(mll)
            models.append(gp)

        model = ModelListGP(*models)

        sampler = self.sampler_cls(
            **self.params.get(self.sampler_cls, {})
        )

        acquisition = self.acq_cls(
            model=model,
            sampler=sampler,
            **self.params.get(self.acq_cls, {})
        )

        candidates_norm, _ = optimize_acqf(
            acquisition,
            bounds=self.bounds_norm,
            q=q,
            **self.params.get("optimize", {})
        )

        return unnormalize(candidates_norm, self.bounds)
