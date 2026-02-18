# libraries
from botorch.models import SingleTaskGP, ModelListGP
from botorch.models.model import Model
from botorch.models.transforms.outcome import Standardize
from gpytorch.mlls import ExactMarginalLogLikelihood
from botorch import fit_gpytorch_mll
from botorch.utils.transforms import normalize

# kernels
from gpytorch.kernels.rbf_kernel import RBFKernel
from gpytorch.kernels.matern_kernel import MaternKernel

# project
from laplace_opt.core.optimizerContext import OptimizationContext
from laplace_opt.model_construction import StrategyStructure


class ModelList(StrategyStructure):
    '''
    Independent-output Gaussian Process model.

    Each output dimension is modeled with an independent SingleTaskGP.
    The resulting models are combined into a ModelListGP for multi-output
    Bayesian optimization.
    '''
    display_name = "Independent GP (ModelList)"
    description = (
        "Independent Gaussian Process for each output dimension.\n"
        "Assumes outputs are conditionally independent given X.\n"
        "Works for Single- and Multi-objectives."
    )

    parameters: dict[str, dict] = {

        "standardize_outputs": {
            "type": bool,
            "default": True,
            "label": "Standardize outputs",
            "description": (
                "Apply per-output standardization before GP training.\n"
                "Improves numerical stability and conditioning."
            )
        },

        "covar_module": {
            "type": dict,
            "default": 0,
            "combo": {
                "RBF": RBFKernel,
                "Matern": MaternKernel
            },
            "label": "Kernel",
            "description" : (
                "Kernel used for each independent Gaussian Process.\n"
                "Defines smoothness and correlation structure of the surrogate model."
            )
        }
    }


    def build_model(self,
                    context: OptimizationContext,
                    **params) -> Model:
        '''
        Construct independent GPs for each output dimension and combine into a ModelListGP.

        Args:
            context: (OptimizationContext)
                Provides training data for each objective and normalization bounds.
            
            **params:
                Additional keyword arguments.

        Returns:
            ModelListGP:
                Fitted multi-output GP model with independent SingleTaskGPs per output.
        '''
        models = []
        
        train_X_list = context.X_by_objective()
        train_Y_list = context.Y_by_objective()
        bounds = context.bounds

        covar_cls = params.get("covar_module", RBFKernel)
        standardize = params.get("standardize_outputs", False)

        for X, Y in zip(train_X_list, train_Y_list):
            X_norm = normalize(X, bounds)

            outcome_transform = (
                Standardize(m=1) if standardize else None
            )

            covar = covar_cls(ard_num_dims=X.shape[-1])

            gp = SingleTaskGP(
                X_norm,
                Y,
                outcome_transform=outcome_transform,
                covar_module=covar,
            )

            mll = ExactMarginalLogLikelihood(gp.likelihood, gp)
            fit_gpytorch_mll(mll)

            models.append(gp)

        return ModelListGP(*models)
