# libraries
import torch
from botorch.acquisition.multi_objective.logei import (
    qLogNoisyExpectedHypervolumeImprovement
)
from botorch.sampling import SobolQMCNormalSampler

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
            "min": 0.0,
            "max": 1.0,
            "label": "alpha",
            "description": (
                "The hyperparameter controlling the approximate non-dominated partitioning.\n"
                "0.0 means exact partitioning; increase with more objectives to reduce computational cost."
            ),
        },
    }

    def build(self, 
              model,
              context: OptimizationContext,
              mc_samples: int,
              alpha: float,
              **kwargs) -> qLogNoisyExpectedHypervolumeImprovement:
        '''
        Construct the qLogNEHVI acquisition function.

        Args:
            model: (Model)
                Fitted BoTorch model representing the surrogate posterior.

            context: (OptimizationContext)
                Optimization context providing access to baseline data,
                reference points, and normalized design points.

            mc_samples: (int)
                Number of Monte Carlo samples used to estimate the acquisition function.

            alpha: (float)
                Trade-off parameter controlling the influence of uncertain points
                in the hypervolume improvement calculation.

            **kwargs:
                Additional keyword arguments forwarded to
                qLogNoisyExpectedHypervolumeImprovement.

        Returns:
            qLogNoisyExpectedHypervolumeImprovement:
                Configured multi-objective acquisition function ready for optimization.
        '''
        
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
            alpha=alpha,
            **kwargs
        )
