# libraries
from botorch.models.model import Model
import torch
from botorch.models import SingleTaskGP, ModelListGP
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
                    **params) -> ModelListGP:
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


    def get_best_results(self,
                         context: OptimizationContext,
                         model: ModelListGP | None,
                         **params):
        '''
        Return best sampled point for each objective using GP posterior mean.

        Args:
            context:
                Optimization context.

        Returns:
            list[dict]:
                A dictionary per objective, gathering its best value,
                the uncertainty and the position when sampling.
        '''
        if not model:
            model = self.build_model(context=context, **params)
        train_X_list = context.X_by_objective()
        bounds = context.bounds

        n_obj = context.n_obj
        maximize = [True] * n_obj
        names = [""] * n_obj
        # names = [obj.name for obj in context.objectives.values()]

        for i, obj in enumerate(context.objectives.values()):
            names[i] = obj.name
            if obj.minimize:
                maximize[i] = False

        best_results = []

        for i, (gp, X) in enumerate(zip(model.models, train_X_list)):

            # normalize like during training
            X_norm = normalize(X, bounds)

            # GP posterior at sampled points
            posterior = gp.posterior(X_norm)

            mean = posterior.mean.squeeze(-1)
            std = posterior.variance.sqrt().squeeze(-1)

            # choose best according to optimization direction
            if maximize[i]:
                best_idx = torch.argmax(mean)
            else:
                best_idx = torch.argmin(mean)

            best_x = X[best_idx]
            best_y = mean[best_idx]
            best_std = std[best_idx]

            best_results.append(
                {
                    "objective": i,
                    "name": names[i],
                    "maximize": maximize[i],
                    "best_x": best_x.tolist(),
                    "best_y": best_y.tolist(),
                    "uncertainty": best_std.tolist(),
                }
            )

        return best_results
            

    # def load_model(self, model, state_dict) -> Model:
    #     model.load_state_dict(state_dict)
    #     model.eval()
    #     return model


    def posterior(self, names: list[str], model: ModelListGP, X_norm: torch.Tensor) -> tuple[dict, dict, dict]:
        posteriors, means, stds = {}, {}, {}

        with torch.no_grad():
            for gp, name in zip(model.models, names):
                post = gp.posterior(X_norm)

                posteriors[name] = post
                means[name] = post.mean.squeeze(-1)
                stds[name] = post.variance.sqrt().squeeze(-1)

        return posteriors, means, stds