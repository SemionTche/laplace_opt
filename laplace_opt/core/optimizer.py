# libraries
from pathlib import Path

from laplace_log import log
from PyQt6.QtCore import pyqtSignal, QObject
import torch
from botorch.optim import optimize_acqf
from botorch.utils.transforms import normalize, unnormalize

# project
from .optimizerContext import OptimizationContext, Observation
from .modelSaver import ModelSaver
from ..utils.json_encoder import (
    json_style, format_candidate_batch
)
from ..utils.build_payload import (
    get_inputs, get_objectives, build_data_payload
)
from ..utils.config_helper import get_from_config
from ..utils.build_opt import(
    build_model, fit_model, 
    build_acq, build_posterior
)


class Optimizer(QObject):
    '''
    Handles candidate generation through model and acquisition build.

    Uses an OptimizationContext to store training data and objectives, 
    supports initialization strategies, and emits new candidates via signals.
    '''
    
    new_candidates = pyqtSignal(dict)     # emit input positions to sample
    max_it_reached = pyqtSignal()         # emit when the max number of step (init + opt) is reached
    new_posterior = pyqtSignal(object)    # emit posterior values to plotting window

    def __init__(self, opt_form: dict):
        '''
        Initialize the Optimizer with a given configuration.

        Args:
            opt_form (dict):
                Dictionary specifying inputs, objectives, initialization, 
                and optimization pipeline parameters.
        '''
        super().__init__()
        self.model_samples = get_from_config(
            module="plot", 
            item="model_sample", 
            default_value=1000, 
            type=int
        )
        self.opt_form = opt_form                        # the optimization form
        self.is_opt: bool = opt_form["opt"]["enabled"]  # whether to make an optimization or not

        # inputs and outputs of the model: {class_name: class()}
        self.inputs_opt: dict = opt_form["inputs"]
        self.objectives_opt: dict = opt_form["obj"]
        self.objective_list = list(self.objectives_opt.values())
        
        self.criterium: dict = opt_form["criterium"]
        self.save_period = self.criterium.get("save_period", 1)
        self.max_it = self.criterium.get("max_iterations", 100)
        self.n_repeats = self.criterium.get("n_repeats", 1)

        # the initialization process
        self.init: dict = opt_form["init"]

        if self.is_opt:
            # strategy and acquisition function
            self.strat: dict = opt_form["opt"]["pipeline"]["strategy"]
            self.acq: dict = opt_form["opt"]["pipeline"]["acquisition"]

        # get the boundaries from the input dictionary
        self.inputs, self.bounds = get_inputs(self.inputs_opt)  # {name: {address:..., bounds:..., position_idx:...}, ... } and 2 x d torch boundaries
        log.debug("Optimization inputs:\n" + json_style(self.inputs))

        # get the objectives from objective dictionary
        self.objectives = get_objectives(self.objectives_opt)  # {address 1: [output key, ...], }
        log.debug("Optimization objectives:\n" + json_style(self.objectives))

        self.suggestion_history = []

        self.context = OptimizationContext(
            bounds=self.bounds,
            objectives=self.objectives_opt,
            inputs=self.inputs_opt
        )

        self.model_saver = ModelSaver(
            save_folder=Path(opt_form["exec"]["saving_path"]), 
            save_period=self.save_period,
            is_saving=bool(opt_form["exec"]["saving_path"])
        )


    def init_opt(self) -> None:
        '''
        Use the initialization refered in the 'opt_form' dictrionary
        to provide the first candidates to be sampled.
        '''
        if not self.opt_form:   # if there is no optimization form
            return              # do not continue
        
        if self.is_opt:                                     # if there is an optimization
            params: dict = self.strat.get("params", {})     # get the parameters from the strategy
            torch.manual_seed(params.get("seed", 0))        # fix the torch seed


        init_cls = self.init["cls"]()      # create an instance of the initialization
        init_params = self.init["params"]  # load the initialization parameters
        
        try:
            self.init_x, self.init_y = init_cls.generate(      # generate the first candidates
                bounds=self.bounds, 
                **init_params
            )

            # if there is no y-elements, then suggest positions
            if self.init_y is None:

                # repeat suggestions
                if self.n_repeats > 1:
                    self.init_x = self.init_x.repeat_interleave(self.n_repeats, dim=0)
                    log.debug("Repetition made on init inputs.")

                # make the payload for the server
                data = build_data_payload(
                    X=self.init_x,
                    inputs=self.inputs,
                    objectives=self.objectives,
                    is_init=True,
                    is_opt=False,
                )

                # print the sample candidates
                log.debug(f"Init suggestion:\n"
                        f"{format_candidate_batch(self.init_x, self.inputs)}"
                )
                
                self.new_candidates.emit(data)  # emit the new candidates to sample


            elif self.init_y is not None and len(self.init_y) > 2:      # else if there are y-elements
            
                log.debug(f"Loaded {len(self.init_x)} previous observations from file.")
                
                for x, y in zip(self.init_x, self.init_y):      # fulfil the context
                    self.context.add_observation(
                        x.double(),
                        y.double(),
                        -1
                    )

                if self.is_opt:                                 # if we want to optimize
                    candidates = self.suggest_candidates()      # generate new candidates

                    payload = build_data_payload(
                        X=candidates.unsqueeze(1),
                        inputs=self.inputs,
                        objectives=self.objectives,
                        is_opt=True,
                        is_init=False,
                    )

                    self.new_candidates.emit(payload)           # emit new candidates
        
        except Exception as e:
            log.error(f"Error during 'init_opt': {e}")


    def suggest_candidates(self) -> torch.Tensor:
        '''Make the suggestion of new candidates.'''
        log.debug("Suggesting new candidates...")

        # get the context values
        X_list = self.context.X_by_objective()
        Y_list = self.context.Y_by_objective()

        if all(X.numel() == 0 for X in X_list):       # verify if all objectives got positions
            log.warning(
                "Some objectives have no data yet; "
                "optimization may be unstable"
            )
    
        for i, (X, Y) in enumerate(zip(X_list, Y_list)):    # for each objective
            log.debug(                                      # print the shape of inputs / outputs for debuging
                f"Objective {i}: "
                f"X={tuple(X.shape)} {X.dtype}, "
                f"Y={tuple(Y.shape)} {Y.dtype}"
            )

        
        model = build_model(            # build the model
            strat=self.strat,
            context=self.context
        )
        self.model_fit = fit_model(     # fit the model
            strat=self.strat,
            model=model
        )
        posterior = build_posterior(    # build the posterior
            model_fit=self.model_fit,
            inputs_opt=self.inputs_opt,
            objectives_opt=self.objectives_opt,
            strat=self.strat,
            bounds=self.bounds,
            model_samples=self.model_samples
        )
        self.new_posterior.emit(posterior)    # emit posterior (for plot window)

        self.acquisition = build_acq(    # build the acquisition function  
            acq=self.acq,
            context=self.context,
            model_fit=self.model_fit
        )

        candidates = self.optimize()  # optimize the model
        
        # repeat samples
        if self.n_repeats > 1:
            candidates = candidates.repeat_interleave(self.n_repeats, dim=0)
            log.debug("Repetition made.")
        
        self.suggestion_history.append(candidates.detach().clone())

        return candidates


    def optimize(self) -> torch.Tensor:
        '''
        Function optimizing the model.
        Return the candidates in physical space.
        '''
        params = self.strat.get("params", {})  

        candidate_norm, acq_value = optimize_acqf(
            acq_function=self.acquisition,
            bounds=normalize(self.bounds, self.bounds),
            q=params.get("q_candidates", 1),
            num_restarts=params.get("num_restarts", None),
            raw_samples=params.get("raw_samples", None),
        )
        log.debug(
            f"Optimization completed. "
            f"Number of candidates: {candidate_norm.shape[0]}"
        )
        
        # value of the candidates for debuging
        candidates_physical = unnormalize(candidate_norm, self.bounds)
        log.debug(f"Candidate (normalized): {candidate_norm}")
        log.debug(f"Candidate (physical): {candidates_physical}")

        return candidates_physical # return the candidates in physical space



    def update_opt(self, observations: list[Observation]) -> None:
        '''
        Add the received data to the context, looks for new suggestions
        and emit a signal to send the new requested points. 
        '''

        if self.context.n_init == -1:                   # if the number of initial points was not set
            self.context.n_init = len(observations)     # this is the initial size
            log.debug(f"Initial batch size received: {self.context.n_init}")

        for obs in observations:
            self.context.add_observation(obs.x, obs.y, obs.shot_number)  # add the observations to the context
        log.debug(f"Context updated: total_observations={len(self.context._observations)}")

        if not self.is_opt:  # if there is no optimization
            log.debug("Optimization disabled: no suggestion available.")
            return           # end here

        log.debug(f"model_saver.counter = {self.model_saver.counter} + 1 (for init), max_it = {self.max_it}")
        if self.max_it > 0:
            if self.max_it <= self.model_saver.counter + 1:
                log.info("Optimization reached the maximum number of (init + optimization) step.")
                self.max_it_reached.emit()
                return

        candidates = self.suggest_candidates()      # else suggest candidates
        best_results = self.compute_best_results()  # compute best results so far

        self.model_saver.save(
            context=self.context, 
            opt_form=self.opt_form, 
            suggestion_history=self.suggestion_history, 
            model=self.model_fit, 
            acq_func=self.acquisition, 
            best_results=best_results,
            is_stop=False
        )
        self.context.step += 1

        # make the payload for the server
        payload = build_data_payload(
            candidates.unsqueeze(1),
            self.inputs,
            self.objectives,
            is_opt=True,
            is_init=False,
        )

        log.debug("Emitting new candidates to server...")
        self.new_candidates.emit(payload)  # look for new candidates


    def compute_best_results(self) -> list[dict[str, int | str | bool | float | list[float]]]:
        strategy_cls = self.strat["cls"]()
        strategy_params = self.strat.get("params", {})
        best_results = strategy_cls.get_best_results(
            context=self.context, model=self.model_fit, **strategy_params
        )
        # print(f"[best results] best_results = {json_style(best_results)}")
        
        return best_results


    def save_end(self) -> None:
        '''
        Save the last observations and model without 
        incrementing the step.
        '''
        self.model_saver.save(
            context=self.context,
            opt_form=self.opt_form,
            suggestion_history=self.suggestion_history,
            model=self.model_fit,
            acq_func=self.acquisition,
            best_results= self.compute_best_results(),
            is_stop=True
        )
        log.info("Final model saved.")


    def set_model_samples(self, model_samples: int) -> None:
        self.model_samples = model_samples