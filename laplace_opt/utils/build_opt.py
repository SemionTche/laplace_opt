'''
This file is made in order to construct
the Bayesian model along as the acquisition
function for the optimizer.
'''
# libraries
from typing import Any

from laplace_log import log
import torch
from botorch.models.model import Model
from botorch.acquisition import AcquisitionFunction
from botorch.utils.transforms import normalize

# project
from ..core.optimizerContext import OptimizationContext
from ..model_construction import (
    StrategyStructure, AcquisitionStructure,
    ObjectiveStructure, InputStructure
)
from ..utils.make_grid import make_grid


def build_model(strat: dict[str, type[StrategyStructure] | dict[str, Any]], 
                context: OptimizationContext) -> Model:
    '''
    Get the model given by the strategy.

    Args:
        strat (dict[str, StrategyStructure | param dict]):
            the strategy structure and parameters.
        
        context (OptimizerContext):
            current data available.
    
    Returns:
        the model produced by the strategy.
    '''
    log.debug(
        f"Building model using strategy "
        f"{strat['cls'].__name__}"
    )
    strategy_cls = strat["cls"]()
    strategy_params = strat.get("params", {})

    model = strategy_cls.build_model(
        context=context,
        **strategy_params,
    )
    log.debug("Model built.")

    return model


def fit_model(strat: dict[str, type[StrategyStructure] | dict[str, Any]], 
              model: Model) -> Model:
    '''
    Fit the model according to the strategy.

    Args:
        strat (dict[str, StrategyStructure | param dict]):
            the strategy structure and parameters.
        
        model (Model):
            the model produced by the strategy.
    
    Returns:
        the model fitted by the strategy.
    '''
    log.debug(
        f"Fitting model using strategy "
        f"{strat['cls'].__name__}"
    )    
    strategy_cls = strat["cls"]()

    model = strategy_cls.fit_model(model)
    log.debug("Model fitted.")

    return model


def build_acq(acq: dict[str, type[AcquisitionStructure] | dict],
              context: OptimizationContext,
              model_fit: Model) -> AcquisitionFunction:
    '''
    Get the acquisition function from acq strategy.

    Args:
        acq (dict[str, AcquisitionStructure | param dict]):
            the acquition structure and parameters.
        
        context (OptimizerContext):
            current data available.
        
        model_fit (Model):
            the fitted model.
    
    Returns:
        the acquisition produced by the acq strategy.
    '''
    log.debug(
        f"Building acquisition using "
        f"{acq['cls'].__name__}"
    )

    acq_cls: AcquisitionStructure = acq["cls"]()
    acq_params = acq.get("params", {})

    acquisition = acq_cls.build_acq(
        model=model_fit,
        context=context,
        **acq_params,
    )
    log.debug("Acquisition built.")

    return acquisition


def build_posterior(model_fit: Model,
                    inputs_opt: dict[str, InputStructure], 
                    objectives_opt: dict[str, ObjectiveStructure],
                    strat: dict[str, StrategyStructure | dict],
                    bounds: torch.Tensor,
                    model_samples: int) -> dict:
    '''
    Get the posterior from the strategy.

    Args:
        model_fit (Model):
            the model produced and fitted by the strategy.
        
        inputs_opt (dict[str, InputStructure]):
            the {class_name: class()} of the inputs.

        objectives_opt (dict[str, ObjectiveStructure]):
            the {class_name: class()} of the objectives.        
        
        strat (dict[str, StrategyStructure | param dict]):
            the strategy structure and parameters.
                        
        bonds (torch.Tensor):
            the torch.Tensor 2 x d input boundaries.
        
        model_samples (int):
            the number of sample per dimension.
    
    Returns:
        the acquisition produced by the acq strategy.
    '''    
    strat_cls = strat["cls"]()
    
    X_grid = make_grid(bounds, n_per_dim=model_samples)
    X_norm = normalize(X_grid, bounds)

    posts, means, stds = strat_cls.posterior(
        model=model_fit,
        X_norm=X_norm
    )
    log.debug(f"Posterior built.")

    input_names = list(inputs_opt.keys())
    obj_names = list(objectives_opt.keys())

    means = dict(zip(obj_names, means))
    stds = dict(zip(obj_names, stds))
    posts = dict(zip(obj_names, posts))
    
    r = {
        "posteriors": posts,
        "means": means,
        "stds": stds,
        "input_list": input_names,
        "x_grid": X_grid,
        "bounds": bounds
    }

    return r


def get_best_results(
        strat: dict[str, type[StrategyStructure] | dict],
        context: OptimizationContext,
        model_fit: Model,) -> list[dict]:

    X = context.X_physical
    X_norm = context.X_normalized

    strat_cls = strat["cls"]()
    _, means, stds = strat_cls.posterior(model_fit, X_norm)

    best_results = []

    for i, (name, obj) in enumerate(context.objectives.items()):
        mean = means[i].reshape(-1)
        std = stds[i].reshape(-1)

        best_idx = mean.argmin() if obj.minimize else mean.argmax()

        best_results.append({
            "objective": i,
            "name": name,
            "maximize": not obj.minimize,
            "best_x": X[best_idx].tolist(),
            "best_y": mean[best_idx].item(),
            "uncertainty": std[best_idx].item(),
        })

    return best_results
