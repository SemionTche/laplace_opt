# libraries
import torch
from botorch.acquisition.multi_objective.logei import (
    qLogNoisyExpectedHypervolumeImprovement
)
from botorch.sampling import SobolQMCNormalSampler
from botorch.models.model import Model

# project
from laplace_opt.core.optimizerContext import OptimizationContext
from laplace_opt.model_construction import AcquisitionStructure


class qLogNEHVI(AcquisitionStructure):
    '''
    Acquisition strategy based on q-Log Noisy Expected Hypervolume Improvement (qLogNEHVI).

    This class defines a Monte Carlo acquisition function for
    batch Bayesian optimization in a noisy multi-objective setting.
    It leverages a quasi-Monte Carlo sampler to estimate the expected
    hypervolume improvement in logarithmic space for improved numerical stability.
    '''
    display_name = "qLogNEHVI"
    description = (
        "Batch Bayesian optimization acquisition for multi-objective,\n"
        "using q-Log Noisy Expected Hypervolume Improvement."
    )

    parameters = {
        "mc_samples": {
            "type": int, 
            "default": 128,
            "label": "MC Samples",
            "description": (
                "Number of Monte Carlo samples used to estimate the acquisition function.\n" 
                "Higher values improve accuracy but increase computation time."
            ),
        },

        "alpha": {
            "type": float, 
            "default": 0.0,
            "step": 0.01,
            "decimals": 2,
            "min": 0.0,
            "max": 1.0,
            "label": "alpha",
            "description": (
                "The hyperparameter controlling the approximate non-dominated partitioning.\n"
                "0.0 means exact partitioning; increase with more objectives to reduce computational cost."
            ),
        },
    }


    def build_acq(self,
                  model: Model,
                  context: OptimizationContext,
                  **kwargs) -> qLogNoisyExpectedHypervolumeImprovement:
        '''
        Construct the qLogNEHVI acquisition function.

        Args:
            model: (Model)
                Fitted BoTorch model representing the surrogate posterior.

            context: (OptimizationContext)
                Optimization context providing access to baseline data,
                reference points, and normalized design points.

            **kwargs:
                Additional keyword arguments.

        Returns:
            qLogNoisyExpectedHypervolumeImprovement:
                Configured multi-objective acquisition function ready for optimization.
        '''
        mc_samples = kwargs.get("mc_samples", 128)
        alpha = kwargs.get("alpha", 0.0)

        sampler = SobolQMCNormalSampler(
            sample_shape=torch.Size([mc_samples])
        )

        ref_point = context.get_ref_point()
        X_baseline_normalized = context.get_X_baseline_normalized()

        return qLogNoisyExpectedHypervolumeImprovement(
            model=model,
            ref_point=ref_point,
            X_baseline=X_baseline_normalized,
            sampler=sampler,
            alpha=alpha
        )
