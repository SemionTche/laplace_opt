import torch
from botorch.acquisition.multi_objective.logei import (
    qLogNoisyExpectedHypervolumeImprovement,
)
from botorch.sampling import SobolQMCNormalSampler

from laplace_opt.core.optimizerContext import OptimizationContext
from laplace_opt.model_construction.acquisitions.acquisition_structure import AcquisitionStructure


class qLogNEHVI(AcquisitionStructure):
    display_name = "qLogNEHVI"

    parameters = {
        "mc_samples": {
            "type": int, 
            "default": 128,
            "description": "",
            "label": "mc_samples"
        },
        "alpha": {
            "type": float, 
            "default": 0.0,
            "min": 0.0,
            "max": 1.0
        },
    }

    def build(
        self,
        model,
        context: OptimizationContext,
        mc_samples: int,
        alpha: float,
        **kwargs,
    ):
        sampler = SobolQMCNormalSampler(
            sample_shape=torch.Size([mc_samples])
        )

        return qLogNoisyExpectedHypervolumeImprovement(
            model=model,
            ref_point=context.compute_ref_point(),
            X_baseline=context.get_X_baseline_normalized(),
            sampler=sampler,
            alpha=alpha,
            **kwargs
        )


    # def get_sampler(self, mc_samples: int):
    #     """
    #     Return a sampler compatible with ModelListGP.
    #     """
    #     return SobolQMCNormalSampler(
    #         sample_shape=torch.Size([mc_samples])
    #     )