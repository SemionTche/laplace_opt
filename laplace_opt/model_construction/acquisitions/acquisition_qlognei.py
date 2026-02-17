# libraries
import torch
from botorch.models.model import Model
from botorch.acquisition.logei import qLogNoisyExpectedImprovement
from botorch.sampling import SobolQMCNormalSampler

# project
from laplace_opt.core.optimizerContext import OptimizationContext
from laplace_opt.model_construction import AcquisitionStructure


class qLogNEI(AcquisitionStructure):
    '''
    Acquisition strategy based on q-Log Noisy Expected Improvement (qLogNEI).

    This class defines a Monte Carlo acquisition function for
    batch Bayesian optimization in the presence of observation noise.
    It leverages a quasi-Monte Carlo sampler to estimate the expected
    improvement in logarithmic space for improved numerical stability.
    '''
    display_name = "qLogNEI"
    description = (
        "Batch Bayesian optimization acquisition for single-objective,\n"
        "using q-Log Noisy Expected Improvement."
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
    }

    def build(self, 
              model: Model,
              context: OptimizationContext,
              mc_samples: int,
              **kwargs) -> qLogNoisyExpectedImprovement:
        '''
        Construct the qLogNEI acquisition function.

        Args:
            model: (Model)
                Fitted BoTorch model representing the surrogate posterior.
            
            context: (OptimizationContext)
                Optimization context providing access to baseline data
                and normalized design points.
            
            mc_samples: (int)
                Number of Monte Carlo samples used to estimate the
                acquisition function.
            
            **kwargs:
                Additional keyword arguments forwarded to
                qLogNoisyExpectedImprovement.

        Returns:
            qLogNoisyExpectedImprovement:
                Configured acquisition function ready for optimization.
        '''
        sampler = SobolQMCNormalSampler(
            sample_shape=torch.Size([mc_samples])
        )
        
        X_baseline_normalized = context.get_X_baseline_normalized()

        return qLogNoisyExpectedImprovement(
            model=model,
            X_baseline=X_baseline_normalized,
            sampler=sampler,
            **kwargs
        )
