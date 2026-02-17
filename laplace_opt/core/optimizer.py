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
from ..utils.json_encoder import (
    json_style, print_evaluations, format_candidate_batch
)
from ..utils.build_payload import (
    get_inputs, get_objectives, build_data_payload
)

class Optimizer(QObject):
    '''
    Manages candidate generation, model building, and acquisition optimization.

    Uses an OptimizationContext to store training data and objectives, 
    supports initialization strategies, and emits new candidates via signals.
    '''
    
    new_candidates = pyqtSignal(dict)

    def __init__(self, opt_form: dict):
        '''
        Initialize the Optimizer with a given configuration.

        Args:
            opt_form: (dict)
                Dictionary specifying inputs, objectives, initialization, 
                and optimization pipeline parameters.
        '''
        super().__init__()         # heritage QObject
        
        self.opt_form = opt_form   # the optimization form

        self.is_opt: bool = opt_form["opt"]["enabled"]  # whether to make an optimization or not

        # inputs and outputs of the model: {class_name: class()}
        self.inputs_opt: dict = opt_form["inputs"]
        self.objectives_opt: dict = opt_form["obj"]
        self.objective_list = list(self.objectives_opt.values())
        
        # the initialization process
        self.init: dict = opt_form["init"]

        if self.is_opt:
            # strategy and acquisition function
            self.strat: dict = opt_form["opt"]["pipeline"]["strategy"]
            self.acq: dict = opt_form["opt"]["pipeline"]["acquisition"]
            params: dict = self.strat.get("params", {})
            save_period = params.get("save_period", 1)
        
        self.inputs, self.bounds = get_inputs(self.inputs_opt) # get the boundaries from the input dictionary
        log.info("Optimization inputs:\n" + json_style(self.inputs))
        
        self.objectives = get_objectives(self.objectives_opt)
        log.info("Optimization objectives:\n" + json_style(self.objectives))

        self.suggestion_history = []

        self.context = OptimizationContext(
            bounds=self.bounds,
            objectives=self.objectives_opt,
        )

        self.model_saver = ModelSaver(
            pathlib.Path(opt_form["exec"]["saving_path"]), 
            save_period or 1,
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
            self.init_x, self.init_y = init_cls.generate(bounds=self.bounds, **init_params)  # generate the first candidates

            # if there is no y-elements
            if self.init_y is None:
                
                # make the payload for the server
                data = build_data_payload(
                    self.init_x,
                    self.inputs,
                    self.objectives,
                    is_init=True,
                    is_opt=False,
                )

                log.info(f"Init suggestion:\n{format_candidate_batch(self.init_x, self.inputs)}") # print the sample candidates
                
                if self.is_opt:
                    params: dict = self.strat.get("params", {})
                    torch.manual_seed(params.get("seed", 0))
                
                self.new_candidates.emit(data)  # emit the new candidates to sample
            
            elif self.init_y is not None and len(self.init_y) > 0:
                print("here")
            
                log.info(f"Loaded {len(self.init_x)} previous observations from file.")
                
                for x, y in zip(self.init_x, self.init_y):
                    self.context.add_observation(
                        x.double(),
                        y.double()
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
        self.strategy_cls = self.strat["cls"]()
        strategy_params = self.strat.get("params", {})

        self.model = self.strategy_cls.build_model(
            context=context,
            **strategy_params,
        )
        log.debug("Model built.")


    def build_acquisition(self, context: OptimizationContext) -> None:
        log.debug(
            f"Building acquisition using "
            f"{self.acq['cls'].__name__}"
        )
        acq_cls = self.acq["cls"]()
        acq_params = self.acq.get("params", {})

        self.acquisition = acq_cls.build(
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
        log.debug(f"Candidate (normalized): {candidate_norm}")
        log.debug(f"Candidate (physical): {unnormalize(candidate_norm, self.bounds)}")

        return unnormalize(candidate_norm, self.bounds) # return the candidates in physical space


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

        for obs in observations:
            self.context.add_observation(obs.x, obs.y)  # add the observations to the context
        log.info(f"Context updated: total_observations={len(self.context._observations)}")

        if not self.is_opt:  # if there is no optimization
            log.debug("Optimization disabled: no suggestion available.")
            return           # end here

        candidates = self.suggest_candidates() # else suggest candidates
        self.model_saver.save(self.context, self.opt_form, self.suggestion_history, self.model)

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


    def _parse_results(self, data: dict) -> list[Observation]:
        '''
        Extract the data received from the server to make
        the observation tensors.
        '''
        observations = []

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
            for i, obj in enumerate(self.objective_list):   # for every objective
                addr = obj.address
                key = obj.output_key

                if addr in outputs and key in outputs[addr]:
                    y_vals[i] = outputs[addr][key][0]       # fill the torch tensor

            observations.append(Observation(x=x, y=y_vals))  # add the observations
        
        log.debug(
            f"Parsed {len(observations)} observations "
            f"(inputs_dim={observations[0].x.numel() if observations else 'n/a'}, "
            f"n_obj={len(self.objective_list)})"
        )

        return observations
