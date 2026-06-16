# libraries
import pathlib
from PyQt6.QtCore import pyqtSignal, QObject

import torch
from botorch.optim import optimize_acqf
from botorch.utils.transforms import normalize, unnormalize

from laplace_log import log

# project
from .optimizerContext import OptimizationContext, Observation
from .modelSaver import ModelSaver
from ..utils.make_grid import make_grid
from ..utils.json_encoder import (
    json_style, print_evaluations, format_candidate_batch
)
from ..utils.build_payload import (
    get_inputs, get_objectives, build_data_payload
)
from ..utils.config_helper import get_from_config
from ..model_construction import (
    StrategyStructure, AcquisitionStructure
)


class Optimizer(QObject):
    '''
    Manages candidate generation, model building, and acquisition optimization.

    Uses an OptimizationContext to store training data and objectives, 
    supports initialization strategies, and emits new candidates via signals.
    '''
    
    new_candidates = pyqtSignal(dict)
    max_it_reached = pyqtSignal()
    new_posterior = pyqtSignal(object)

    def __init__(self, opt_form: dict):
        '''
        Initialize the Optimizer with a given configuration.

        Args:
            opt_form: (dict)
                Dictionary specifying inputs, objectives, initialization, 
                and optimization pipeline parameters.
        '''
        super().__init__()         # heritage QObject
        self.model_samples = get_from_config(
            module="plot", 
            item="model_sample", 
            default_value=1000, 
            type=int
        )
        self.opt_form = opt_form   # the optimization form
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
        
        self.inputs, self.bounds = get_inputs(self.inputs_opt) # get the boundaries from the input dictionary
        log.info("Optimization inputs:\n" + json_style(self.inputs))
        
        self.objectives = get_objectives(self.objectives_opt)
        log.info("Optimization objectives:\n" + json_style(self.objectives))

        self.suggestion_history = []

        self.context = OptimizationContext(
            bounds=self.bounds,
            objectives=self.objectives_opt,
            inputs=self.inputs_opt
        )

        self.model_saver = ModelSaver(
            pathlib.Path(opt_form["exec"]["saving_path"]), 
            self.save_period,
            bool(opt_form["exec"]["saving_path"])
        )


    def init_opt(self) -> None:
        '''
        Use the initialization refered in the 'opt_form' dictrionary
        to provide the first candidates to sampled.
        '''
        if not self.opt_form:   # if there is no optimization form
            return              # do not continue
        
        init_cls = self.init["cls"]()      # create an instance of the initialization
        init_params = self.init["params"]  # load the initialization parameters
        
        try:
            self.init_x, self.init_y = init_cls.generate(  # generate the first candidates
                bounds=self.bounds, 
                **init_params
            )

            # if there is no y-elements
            if self.init_y is None:

                # repeat suggestions
                if self.n_repeats > 1:
                    self.init_x = self.init_x.repeat_interleave(self.n_repeats, dim=0)
                    log.debug("Repetition made on inputs.")

                # make the payload for the server
                data = build_data_payload(
                    self.init_x,
                    self.inputs,
                    self.objectives,
                    is_init=True,
                    is_opt=False,
                )

                log.info(f"Init suggestion:\n"
                            f"{format_candidate_batch(self.init_x, self.inputs)}") # print the sample candidates
                
                if self.is_opt:
                    params: dict = self.strat.get("params", {})
                    torch.manual_seed(params.get("seed", 0))
                
                self.new_candidates.emit(data)  # emit the new candidates to sample
            
            elif self.init_y is not None and len(self.init_y) > 0:
            
                log.info(f"Loaded {len(self.init_x)} previous observations from file.")
                
                for x, y in zip(self.init_x, self.init_y):
                    self.context.add_observation(
                        x.double(),
                        y.double(),
                        -1
                    )

                if self.is_opt:
                    candidates = self.suggest_candidates()

                    payload = build_data_payload(
                        candidates.unsqueeze(1),
                        self.inputs,
                        self.objectives,
                        is_opt=True,
                        is_init=False,
                    )

                    self.new_candidates.emit(payload)
        except Exception as e:
            log.error(f"Error: {e}")

    
    def build_model(self, context: OptimizationContext) -> None:
        log.debug(
            f"Building model using strategy "
            f"{self.strat['cls'].__name__}"
        )
        self.strategy_cls: StrategyStructure = self.strat["cls"]()
        strategy_params = self.strat.get("params", {})

        self.model = self.strategy_cls.build_model(
            context=context,
            **strategy_params,
        )
        self.model = self.strategy_cls.fit_model(self.model)
        log.debug("Model built.")
        self.build_posterior(self.model, self.strategy_cls)

    
    def build_posterior(self, model, strategy) -> None:
        names = [obj.__class__.__qualname__ for obj in self.objective_list]
        print(f'names in post = {names}')

        X_grid = make_grid(self.bounds, n_per_dim=self.model_samples)
        X_norm = normalize(X_grid, self.bounds)
        
        posts, means, stds = strategy.posterior(
            names=names,
            model=model,
            X_norm=X_norm
        )
        log.debug(f"Posterior built.")
        input_names = [inp.__class__.__qualname__ for inp in self.inputs_opt.values()]
        print(f"input names in post = {input_names}")
        posterior = {
            "means": means,
            "stds": stds,
            "input_list": input_names,
            "x_grid": X_grid,
            "bounds": self.bounds
        }
        self.new_posterior.emit(posterior)



    def build_acquisition(self, context: OptimizationContext) -> None:
        log.debug(
            f"Building acquisition using "
            f"{self.acq['cls'].__name__}"
        )
        acq_cls: AcquisitionStructure = self.acq["cls"]()
        acq_params = self.acq.get("params", {})

        self.acquisition = acq_cls.build_acq(
            model=self.model,
            context=context,
            **acq_params,
        )
        log.debug("Acquisition built.")


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
        log.info(
            f"Optimization completed. "
            f"Number of candidates: {params.get('q_candidates', 1)}"
        )
        
        # value of the candidates for debuging
        candidates_physical = unnormalize(candidate_norm, self.bounds)
        log.debug(f"Candidate (normalized): {candidate_norm}")
        log.debug(f"Candidate (physical): {candidates_physical}")

        return candidates_physical # return the candidates in physical space


    def suggest_candidates(self) -> torch.Tensor:
        '''
        Make the suggestion of new candidates.
        '''
        log.info("Suggesting new candidates...")

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

        # build the model
        self.build_model(self.context)
        self.build_acquisition(self.context)

        candidates = self.optimize()  # optimize the model
        
        # repeat samples
        if self.n_repeats > 1:
            candidates = candidates.repeat_interleave(self.n_repeats, dim=0)
            log.debug("Repetition made.")

        for i, gp in enumerate(self.model.models):
            print(f"\nHyperparameters")
            print(f"Objective {i}")
            print("lengthscale:", gp.covar_module.lengthscale.detach())
            print("noise:", gp.likelihood.noise.detach())
        
        self.suggestion_history.append(candidates.detach().clone())

        return candidates


    def update_opt(self, data: dict) -> None:
        '''
        Add the received data to the context, looks for new suggestions
        and emit a signal to send the new requested points. 
        '''
        log.info(f"Data received:\n" + 
                 print_evaluations(data.get("results", []), self.inputs)
        )
        
        observations = self._parse_results(data)   # make the tensor observations

        if self.context.n_init == -1:                   # if the number of initial points was not set
            self.context.n_init = len(observations)     # this is the initial size
            log.info(f"Initial batch size received: {self.context.n_init}")

        for obs in observations:
            self.context.add_observation(obs.x, obs.y, obs.shot_number)  # add the observations to the context
        log.info(f"Context updated: total_observations={len(self.context._observations)}")

        if not self.is_opt:  # if there is no optimization
            log.debug("Optimization disabled: no suggestion available.")
            return           # end here

        log.debug(f"model_saver.counter = {self.model_saver.counter} + 1 (for init), max_it = {self.max_it}")
        if self.max_it > 0:
            if self.max_it <= self.model_saver.counter + 1:
                log.info("Optimization reached the maximum number of (init + optimization) step.")
                self.max_it_reached.emit()
                return

        candidates = self.suggest_candidates() # else suggest candidates

        best_results = self.compute_best_results()  # compute best results so far

        self.model_saver.save(
            context=self.context, 
            opt_form=self.opt_form, 
            suggestion_history=self.suggestion_history, 
            model=self.model, 
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

        log.info("Emitting new candidates to server...")
        self.new_candidates.emit(payload)  # look for new candidates


    def compute_best_results(self) -> list[dict[str, int | str | bool | float | list[float]]]:
        strategy_params = self.strat.get("params", {})
        best_results = self.strategy_cls.get_best_results(
            context=self.context, model=self.model, **strategy_params
        )
        print(f"[best results] best_results = {json_style(best_results)}")
        
        return best_results


    def _parse_results(self, data: dict) -> list[Observation]:
        '''
        Extract the data received from the server to make
        the observation tensors.
        '''
        observations = []
        print(f"in parse, data = {data}")
        print(f"and results = {data['results']}")
        for r in data["results"]:  # for every results
            
            # build x (the input position)
            x_vals = []
            for name in self.inputs:
                info = self.inputs[name]
                addr = info["address"]
                pos = info["position_index"]
                x_vals.append(r["inputs"][addr][pos])

            x = torch.tensor(x_vals, dtype=torch.double)

            # build y (the objective values)
            y_vals = torch.full(               # make the 'nan' torch tensor
                (len(self.objective_list),), 
                float("nan"),
                dtype=torch.double
            )

            outputs = r["outputs"]
            print(f"outputs = {outputs} for results = {r}")
            for i, obj in enumerate(self.objective_list):   # for every objective
                addr = obj.address
                key = obj.output_key

                if addr in outputs and key in outputs[addr]:
                    y_vals[i] = outputs[addr][key]#[0]       # fill the torch tensor
            
            shot_number = r["shot_number_from_master"]

            observations.append(Observation(x=x, y=y_vals, shot_number=shot_number))  # add the observations
        
        log.debug(
            f"Parsed {len(observations)} observations "
            f"(inputs_dim={observations[0].x.numel() if observations else 'n/a'}, "
            f"n_obj={len(self.objective_list)})"
        )

        return observations


    def save_end(self) -> None:
        '''
        Save the last observations and model without 
        incrementing the step.
        '''
        self.model_saver.save(
            context=self.context,
            opt_form=self.opt_form,
            suggestion_history=self.suggestion_history,
            model=self.model,
            acq_func=self.acquisition,
            best_results= self.compute_best_results(),
            is_stop=True
        )
        log.info("Final model saved.")


    def set_model_samples(self, model_samples: int) -> None:
        self.model_samples = model_samples