# libraries
from PyQt6.QtCore import pyqtSignal, QObject

import torch
from botorch.optim import optimize_acqf
from botorch.utils.transforms import normalize, unnormalize

from laplace_log import log

# project
from core.optimizerContext import OptimizationContext
from utils.build_payload import (
    get_inputs, get_objectives, build_data_payload
)

class Optimizer(QObject):
    '''
    '''
    
    new_candidates = pyqtSignal(dict)

    def __init__(self, opt_form: dict):
        '''
        '''
        super().__init__()          # heritage QObject
        
        self.opt_form = opt_form   # the optimization formular

        self.is_opt: bool = opt_form["opt"]["enabled"]  # whether to make an optimization or not

        # inputs and outputs of the model
        self.inputs_opt: dict = opt_form["inputs"]
        self.objectives_opt: dict = opt_form["obj"]
        
        self.init: dict = opt_form["init"]  # the initialization process
        self.objective_list = list(self.objectives_opt.values())
        

        if self.is_opt:
            self.strat: dict = opt_form["opt"]["pipeline"]["strategy"]
            self.acq: dict = opt_form["opt"]["pipeline"]["acquisition"]

            self.model = None
            self.train_X_list = None
            self.train_Y_list = None

        
        self.inputs, self.bounds = get_inputs(self.inputs_opt) # get the boundaries from the input dictionary
        print(self.inputs)
        self.objective = get_objectives(self.objectives_opt)

        self.train_X_list_raw = None  # list of lists
        self.train_Y_list_raw = None
        self.context = None


    def init_opt(self):
        '''
        Use the initialization refered in the 'opt_form' dictrionary.
        '''
        init_cls = self.init["cls"]()
        init_params = self.init["params"]

        self.init_x = init_cls.generate(bounds=self.bounds, **init_params)  # generate the first candidates

        data = build_data_payload(                       # make the payload for the server
            self.init_x,
            self.inputs,
            self.objective,
            is_init=True,
            is_opt=False,
        )

        print(f"Sobol suggestion:\n{self.format_print(self.init_x, self.inputs)}") # print the sample candidates

        self.new_candidates.emit(data)


    def format_print(self, X: torch.Tensor, inputs: dict) -> str:
        '''
        Print the values that each input should take. Use a X 'torch.Tensor'
        for the values and a 'inputs' for the input addresses.
        '''
        addresses = [v["address"] for v in inputs.values()]  # make a list of addresses
        position_index = [v["position_index"] for v in inputs.values()]

        lines = []
        for i in range(X.shape[0]):                            # for each sample
            lines.append(f"batch {i + 1}:")                     # print which sample it is
            for j in range(X.shape[1]):                          # for each candidate
                coords = ", ".join(
                    f"{addr}|{pos}={X[i, j, k].item():.6g}"            # for each input, address = value
                    for k, (addr, pos) in enumerate(zip(addresses, position_index))
                )
                lines.append(f"  Candidate {j + 1}: {coords}")   # print the candidate
        
        return "\n".join(lines)
    
    
    def build_model(self, context: OptimizationContext) -> None:
        self.strategy_cls = self.strat["cls"]()
        strategy_params = self.strat.get("params", {})

        self.model = self.strategy_cls.build_model(
            context=context,
            **strategy_params,
        )
    
    def build_acquisition(self, context) -> None:
        acq_cls = self.acq["cls"]()
        acq_params = self.acq.get("params", {})

        self.acquisition = acq_cls.build(
            model=self.model,
            context=context,
            **acq_params,
        )


    def optimize(self):
        params = self.strat.get("params", {})

        candidate_norm, acq_value = optimize_acqf(
            acq_function=self.acquisition,
            bounds=normalize(self.bounds, self.bounds),
            q=params.get("q_candidates", 1),
            num_restarts=params.get("num_restarts", None),
            raw_samples=params.get("raw_samples", None),
        )
        print(f"unnormalized candidates = {unnormalize(candidate_norm, self.bounds)}")
        print(f"candidates = {candidate_norm}")
        return unnormalize(candidate_norm, self.bounds)


    def suggest_next_points(self) -> torch.Tensor:
        '''
        High-level API used by UI / server.
        '''
        # if self.train_X_list is None:
        #     raise RuntimeError("No training data available.")

        # # at least one objective must have data
        # if not any(len(X) > 0 for X in self.train_X_list):
        #     raise RuntimeError("No objective has observations.")
        
        if self.train_X_list_raw is None or not any(self.train_X_list_raw):
            raise RuntimeError("No training data available.")
        
        # self.context = OptimizationContext(
        #     train_X_list=self.train_X_list,
        #     train_Y_list=self.train_Y_list,
        #     bounds=self.bounds,
        #     objectives=self.objectives_opt,
        # )

        self.build_model(self.context)
        self.build_acquisition(self.context)
        return self.optimize()


    # def runtime_args(self, cls) -> dict:
    #     runtime_inputs = {}

    #     if "sampler" in cls.requires:
    #         runtime_inputs["sampler"] = cls.get_sampler(self.acq.get("params", {})["mc_samples"])

    #     if "X_baseline" in cls.requires:
    #         Xb = self.get_X_baseline()
    #         runtime_inputs["X_baseline"] = normalize(Xb, self.bounds)

    #     if "ref_point" in cls.requires:
    #         runtime_inputs["ref_point"] = self.compute_ref_point()

    #     return runtime_inputs

    def _sync_context(self):
        '''Convert raw lists into tensors and update OptimizationContext.'''
        train_X_list = []
        train_Y_list = []

        for X_raw, Y_raw in zip(self.train_X_list_raw, self.train_Y_list_raw):
            if not X_raw:
                train_X_list.append(torch.empty(0, self.bounds.shape[1], dtype=torch.float64))
                train_Y_list.append(torch.empty(0, 1, dtype=torch.float64))
            else:
                train_X_list.append(torch.stack(X_raw))
                train_Y_list.append(torch.stack(Y_raw))

        self.train_X_list = train_X_list
        self.train_Y_list = train_Y_list

        if self.context is None:
            # build context for the first time
            self.context = OptimizationContext(
                train_X_list=self.train_X_list,
                train_Y_list=self.train_Y_list,
                bounds=self.bounds,
                objectives=self.objectives_opt,
            )
        else:
            # update tensors in existing context
            self.context.train_X_list = self.train_X_list
            self.context.train_Y_list = self.train_Y_list


    def update_opt(self, data: dict):
        self._update_training_data(data)

        if self.is_opt:
            candidates = self.suggest_next_points()
            ext = candidates.unsqueeze(1)
            print(f"candidates are : {candidates}, candidates updated = {ext}")
            
            data = build_data_payload(ext, self.inputs, self.objective, is_opt=True, is_init=False)
            print(f"data build payload candidates = {data}")
            self.new_candidates.emit(data)
            # self.send_to_server(candidates)


    def _update_training_data(self, data: dict) -> None:
        print(f"[CMD_OPT] data = {data}")
        results = data["results"]

        # Lazy init of raw lists
        if self.train_X_list_raw is None:
            n_obj = len(self.objective_list)
            self.train_X_list_raw = [[] for _ in range(n_obj)]
            self.train_Y_list_raw = [[] for _ in range(n_obj)]

        for r in results:
            # rebuild x in deterministic order
            x_vals = []
            for name in self.inputs:
                info = self.inputs[name]
                addr = info["address"]
                pos = info["position_index"]
                x_vals.append(r["inputs"][addr][pos])

            x = torch.tensor(x_vals, dtype=torch.float64)

            outputs = r["outputs"]

            for obj_idx, obj in enumerate(self.objective_list):
                addr = obj.address
                key = obj.output_key

                if addr not in outputs or key not in outputs[addr]:
                    continue

                values = outputs[addr][key]
                for v in values:
                    self.train_X_list_raw[obj_idx].append(x)
                    self.train_Y_list_raw[obj_idx].append(
                        torch.tensor([v], dtype=torch.float64)
                    )

        # Build / update context
        self._sync_context()
