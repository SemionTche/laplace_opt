import torch
from botorch.acquisition.multi_objective.logei import (
    qLogNoisyExpectedHypervolumeImprovement,
)
from botorch.sampling import SobolQMCNormalSampler

from model_construction.acquisitions.acquisition_structure import AcquisitionStructure


class qLogNEHVI(AcquisitionStructure):
    display_name = "qLogNEHVI"

    parameters = {
        "mc_samples": {
            "type": int, 
            "default": 128
        },
        "alpha": {
            "type": float, 
            "default": 0.0,
            "min": 0.0,
            "max": 1.0
        },
    }

    requires = {"ref_point", "X_baseline", "sampler"}

    def build(
        self,
        model,
        sampler,
        ref_point: torch.Tensor,
        X_baseline: torch.Tensor,
        alpha: float,
        **kwargs,
    ):
        return qLogNoisyExpectedHypervolumeImprovement(
            model=model,
            ref_point=ref_point,
            X_baseline=X_baseline,
            sampler=sampler,
            alpha=alpha,
        )


    def get_sampler(self, mc_samples: int):
        """
        Return a sampler compatible with ModelListGP.
        """
        return SobolQMCNormalSampler(
            sample_shape=torch.Size([mc_samples])
        )