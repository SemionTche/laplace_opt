# libraries
from botorch.models import SingleTaskGP, ModelListGP
from torch.nn import Module
from botorch.models.transforms.outcome import Standardize
from gpytorch.mlls import ExactMarginalLogLikelihood
from botorch import fit_gpytorch_mll
from botorch.utils.transforms import normalize
from botorch.models.transforms.input import Normalize

    # kernels
from gpytorch.kernels.rbf_kernel import RBFKernel
from gpytorch.kernels.matern_kernel import MaternKernel

# project
from laplace_opt.core.optimizerContext import OptimizationContext
from laplace_opt.model_construction.strategies.strategy_structure import StrategyStructure


class ModelList(StrategyStructure):
    '''
    Independent-output Gaussian Process model.

    Each output dimension is modeled with an independent SingleTaskGP.
    The resulting models are combined into a ModelListGP.
    '''

    display_name = "Independent GP (ModelList)"
    description = (
        "Independent Gaussian Process for each output dimension. "
        "Assumes outputs are conditionally independent given X."
    )

    parameters: dict[str, dict] = {

        "standardize_outputs": {
            "type": bool,
            "default": True,
            "label": "Standardize outputs",
            "description": "Apply outcome standardization per output GP",
        },

        # "covar_module": {
        #     "type": dict,
        #     "default": 0,
        #     "combo": {
        #         "RBF": RBFKernel,
        #         "Matern": MaternKernel
        #     },
        #     "label": "Kernel",
        #     "description" : ""
        # }
    }

    def build_model(self, context: OptimizationContext, **params) -> Module:
        models = []
        
        train_X_list = context.X_by_objective()
        train_Y_list = context.Y_by_objective()
        bounds = context.bounds

        standardize = params.get("standardize_outputs", False)

        for X, Y in zip(train_X_list, train_Y_list):
            X_norm = normalize(X, bounds)

            outcome_transform = (
                Standardize(m=1) if standardize else None
            )

            gp = SingleTaskGP(      # by default use RBF Kernel
                X_norm,
                # X,
                Y,
                outcome_transform=outcome_transform,
                # input_transform=Normalize(
                #     d=X.shape[-1],
                #     bounds=bounds,
                # ),
            )

            mll = ExactMarginalLogLikelihood(gp.likelihood, gp)
            fit_gpytorch_mll(mll)

            models.append(gp)

        return ModelListGP(*models)
