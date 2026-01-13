# libraries
from botorch.models import SingleTaskGP, ModelListGP
from botorch.models.transforms.outcome import Standardize
from gpytorch.mlls import ExactMarginalLogLikelihood
from botorch import fit_gpytorch_mll
from botorch.utils.transforms import normalize
from botorch.models.transforms.input import Normalize

    # kernels
from gpytorch.kernels.rbf_kernel import RBFKernel
from gpytorch.kernels.matern_kernel import MaternKernel

# project
from core.optimizerContext import OptimizationContext
from model_construction.strategies.strategy_structure import StrategyStructure


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

    def build_model(self, context: OptimizationContext, **params):
        models = []
        
        train_X_list = context.train_X_list
        train_Y_list = context.train_Y_list
        bounds = context.bounds

        standardize = params.get("standardize_outputs", None)

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
    

    # # ------------------------------------------------------------------
    # # Model construction
    # # ------------------------------------------------------------------
    # def build_model(
    #     self,
    #     train_X: torch.Tensor,
    #     train_Y: torch.Tensor,
    #     bounds: torch.Tensor,
    #     **params,
    # ):
    #     '''
    #     Build and fit a ModelListGP composed of independent SingleTaskGPs.
    #     '''

    #     # normalize inputs
    #     X_norm = normalize(train_X, bounds)

    #     standardize = params.get("standardize_outputs", True)
    #     noise = params.get("noise", None)

    #     models: List[SingleTaskGP] = []

    #     for i in range(train_Y.shape[-1]):
    #         Y_i = train_Y[:, i : i + 1]

    #         outcome_transform = (
    #             Standardize(m=1) if standardize else None
    #         )

    #         if noise is None:
    #             gp = SingleTaskGP(
    #                 X_norm,
    #                 Y_i,
    #                 outcome_transform=outcome_transform,
    #             )
    #         else:
    #             gp = SingleTaskGP(
    #                 X_norm,
    #                 Y_i,
    #                 noise=torch.full_like(Y_i, noise),
    #                 outcome_transform=outcome_transform,
    #             )

    #         mll = ExactMarginalLogLikelihood(gp.likelihood, gp)
    #         fit_gpytorch_mll(mll)

    #         models.append(gp)

    #     return ModelListGP(*models)
