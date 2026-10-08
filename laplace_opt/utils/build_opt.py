'''
This file is made in order to construct
the Bayesian model along as the acquisition
function for the optimizer.
'''
# libraries
from laplace_log import log

from torch import Tensor
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


def build_model(strat: dict[str, type[StrategyStructure] | dict], 
                context: OptimizationContext) -> Model:
    log.debug(
        f"Building model using strategy "
        f"{strat['cls'].__name__}"
    )
    strategy_cls: StrategyStructure = strat["cls"]()
    strategy_params = strat.get("params", {})

    model = strategy_cls.build_model(
        context=context,
        **strategy_params,
    )
    log.debug("Model built.")

    return model


def fit_model(strat: dict[str, type[StrategyStructure] | dict], 
              model: Model) -> Model:
    log.debug(
        f"Fitting model using strategy "
        f"{strat['cls'].__name__}"
    )    
    strategy_cls: StrategyStructure = strat["cls"]()

    model = strategy_cls.fit_model(model)
    log.debug("Model fitted.")

    return model


def build_acq(acq: dict[str, type[AcquisitionStructure] | dict],
              context: OptimizationContext,
              model_fit: Model) -> AcquisitionFunction:
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
                    bounds: Tensor,
                    model_samples: int) -> dict:
    
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