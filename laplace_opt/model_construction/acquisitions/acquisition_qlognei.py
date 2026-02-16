import torch
from botorch.acquisition.logei import qLogNoisyExpectedImprovement
from botorch.sampling import SobolQMCNormalSampler

from laplace_opt.core.optimizerContext import OptimizationContext
from laplace_opt.model_construction.acquisitions.acquisition_structure import AcquisitionStructure


class qLogNEI(AcquisitionStructure):
    display_name = "qLogNEI"

    parameters = {
        "mc_samples": {
            "type": int, 
            "default": 128,
            "description": "Monte Carlo sample size",
            "label": "mc_samples"
        },
    }

    def build(
        self,
        model,
        context: OptimizationContext,
        mc_samples: int,
        **kwargs,
    ):
        sampler = SobolQMCNormalSampler(
            sample_shape=torch.Size([mc_samples])
        )

        return qLogNoisyExpectedImprovement(
            model=model,
            X_baseline=context.get_X_baseline_normalized(),
            sampler=sampler,
            **kwargs
        )
