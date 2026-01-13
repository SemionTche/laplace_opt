import torch


from botorch.optim import optimize_acqf
from botorch.utils.transforms import normalize, unnormalize

from core.optimizerContext import OptimizationContext

class Optimizer:

    def __init__(self, opt_form: dict):
        self.opt_form = opt_form   # the optimization formular

        self.is_opt: bool = opt_form["opt"]["enabled"]  # whether to make an optimization or not

        # inputs and outputs of the model
        self.inputs: dict = opt_form["inputs"]
        self.objectives: dict = opt_form["obj"]
        
        self.init: dict = opt_form["init"]  # the initialization process
        
        if self.is_opt:
            self.strategy: dict = opt_form["opt"]["pipeline"]["strategy"]
            self.acq: dict = opt_form["opt"]["pipeline"]["acquisition"]

            self.model = None
            self.train_X_list = None
            self.train_Y_list = None

            # One dataset per objective
            # self.train_X_list: list[torch.Tensor]  # each (n_i, d)
            # self.train_Y_list: list[torch.Tensor]  # each (n_i, 1)

        self.bounds_dict, self.bounds = self.get_boundaries() # get the boundaries from the input dictionary


    def init_opt(self):
        '''
        Use the initialization refered in the 'opt_form' dictrionary.
        '''
        init_cls = self.init["cls"]()
        init_params = self.init["params"]

        self.init_x = init_cls.generate(bounds=self.bounds, **init_params)  # generate the first points to sample

        data = self.build_data_payload(                       # make the payload for the server
            self.init_x,
            self.bounds_dict,
            is_init=True,
            is_opt=False,
        )

        print("Sobol suggestion:\n", self.format_print(self.init_x, self.bounds_dict)) # print the sample candidates

        return data


    def build_data_payload(self, X: torch.Tensor, 
                        bounds_dict: dict,
                        *,
                        is_init: bool,
                        is_opt: bool) -> dict:
        '''
        Build the payload dictionary to be transmited through
        the server.

            Args:
                X: (torch.Tensor)
                    the sample candidates to sample of shape (n, q, d).
                
                bounds_dict: (dict)
                    the input main informations: {name: {"bounds": ..., "address": ...}}

                is_init: (bool)
                    indicating if it is the initialization suggested points.
                
                is_opt: (bool)
                    indicating if it is the optimization suggested points.
        '''
        payload = {}

        # make a list of addresses (one per dimension)
        addresses = [v["address"] for v in bounds_dict.values()]

        # ensure CPU tensor for serialization
        X = X.cpu()

        samples = []

        for i in range(X.shape[0]):        # for each batch
            for j in range(X.shape[1]):    # for each candidate

                inputs = {}                # NEW dict per sample

                for k, addr in enumerate(addresses):  # for each dimension

                    # initialize list if address already exists
                    if addr not in inputs:
                        inputs[addr] = []

                    # append the value corresponding to this DOF
                    inputs[addr].append(X[i, j, k].item())

                # add the sample to the list
                samples.append({
                    "batch": i,
                    "candidate": j,
                    "inputs": inputs,
                })

        payload = {
            "is_init": is_init,
            "is_opt": is_opt,
            "samples": samples,
        }

        return payload


    def get_boundaries(self) -> tuple[dict[str, tuple], torch.Tensor]:
        '''
        Helper that extract the boundaries from the 'input' dictionary
        stored in the optimization form.
        
        Return both a dictionary where the boundaries and input addresses
        are stored using there names and a 'Torch.Tensor' to gather the 
        boundaries.
        '''
        bounds = []        # gather the boundaries
        bounds_dict = {}   # information about the inputs
                
        for name, cls in self.inputs.items():  # for each element
            bounds.append(cls.bounds)     # add the boundaries in the list
            # create the field to gather the address and the boundaries
            bounds_dict[name] = {
                "address": cls.address, 
                "bounds": cls.bounds, 
                "position_index": cls.position_index
            }
        
        bounds = torch.Tensor(bounds).T   # convert the list to a tensor. The tensor must be 2 x d (d = input dimension)
        
        return bounds_dict, bounds


    def format_print(self, X: torch.Tensor, bounds_dict: dict) -> str:
        '''
        Print the values that each input should take. Use a X 'torch.Tensor'
        for the values and a 'bounds_dict' for the input addresses.
        '''
        addresses = [v["address"] for v in bounds_dict.values()]  # make a list of addresses
        position_index = [v["position_index"] for v in bounds_dict.values()]

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
        self.strategy_cls = self.strategy["cls"]()
        strategy_params = self.strategy.get("params", {})

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
        params = self.strategy.get("params", {})

        candidate_norm, acq_value = optimize_acqf(
            acq_function=self.acquisition,
            bounds=normalize(self.bounds, self.bounds),
            q=params.get("q_candidates", 1),
            num_restarts=params.get("num_restarts", None),
            raw_samples=params.get("raw_samples", None),
        )

        return unnormalize(candidate_norm, self.bounds)


    def suggest_next_points(self) -> torch.Tensor:
        """
        High-level API used by UI / server.
        """
        if self.train_X_list is None:
            raise RuntimeError("No training data available.")

        # at least one objective must have data
        if not any(len(X) > 0 for X in self.train_X_list):
            raise RuntimeError("No objective has observations.")
        
        self.context = OptimizationContext(
            train_X_list=self.train_X_list,
            train_Y_list=self.train_Y_list,
            bounds=self.bounds,
            objectives=self.objectives,
        )

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


    def update_opt(self, data: dict):
        self._update_training_data(data)

        if self.is_opt:
            candidates = self.suggest_next_points()
            print(f"candidates are : {candidates}")
            # self.send_to_server(candidates)


    def _update_training_data(self, data: dict) -> None:
        print(f"[CMD_OPT] data = {data}")
        results = data["results"]

        # Lazy init: one list per objective
        if self.train_X_list is None:
            num_obj = len(results[0]["output"])
            self.train_X_list = [[] for _ in range(num_obj)]
            self.train_Y_list = [[] for _ in range(num_obj)]

        for r in results:
            x = torch.tensor(
                next(iter(r["inputs"].values())),
                dtype=torch.float64,
            )

            for obj_idx, y_val in enumerate(r["output"]):
                if y_val is None:
                    continue

                self.train_X_list[obj_idx].append(x)
                self.train_Y_list[obj_idx].append(
                    torch.tensor([y_val], dtype=torch.float64)
                )

        # Convert lists → tensors
        for i in range(len(self.train_X_list)):
            if len(self.train_X_list[i]) == 0:
                continue

            self.train_X_list[i] = torch.stack(self.train_X_list[i], dim=0)
            self.train_Y_list[i] = torch.stack(self.train_Y_list[i], dim=0)

        # print("[OPT] train_X_list status:")
        # for i, X in enumerate(self.train_X_list):
        #     print(f"  train_X_list[{i}] = {X}")

        # print("[OPT] train_Y_list status:")
        # for i, Y in enumerate(self.train_Y_list):
        #     print(f"  train_Y_list[{i}] = {Y}")

    # def update_opt(self, data: dict) -> None:
    #     print(f"[CMD_OPT] data = {data}")
    #     results = data["results"]

    #     # Lazy init: one list per objective
    #     if self.train_X_list is None:
    #         num_obj = len(results[0]["output"])
    #         self.train_X_list = [[] for _ in range(num_obj)]
    #         self.train_Y_list = [[] for _ in range(num_obj)]

    #     for r in results:
    #         x = torch.tensor(
    #             next(iter(r["inputs"].values())),
    #             dtype=torch.float32,
    #         )

    #         for obj_idx, y_val in enumerate(r["output"]):
    #             if y_val is None:
    #                 continue

    #             self.train_X_list[obj_idx].append(x)
    #             self.train_Y_list[obj_idx].append(
    #                 torch.tensor([y_val], dtype=torch.float32)
    #             )

    #     # Convert lists → tensors
    #     for i in range(len(self.train_X_list)):
    #         if len(self.train_X_list[i]) == 0:
    #             continue

    #         self.train_X_list[i] = torch.stack(self.train_X_list[i], dim=0)
    #         self.train_Y_list[i] = torch.stack(self.train_Y_list[i], dim=0)

    #     print("[OPT] train_X_list status:")
    #     for i, X in enumerate(self.train_X_list):
    #         print(f"  train_X_list[{i}] = {X}")

    #     print("[OPT] train_Y_list status:")
    #     for i, Y in enumerate(self.train_Y_list):
    #         print(f"  train_Y_list[{i}] = {Y}")

    #     self.build_strategy_model()



    # def build_strategy_model(self) -> None:
    #     """
    #     Instantiate the optimization strategy and build its model
    #     using the current training data.
    #     """
    #     if not self.is_opt:
    #         return

    #     if self.train_X_list is None or self.train_Y_list is None:
    #         return

    #     # Require at least one objective with data
    #     if not any(len(X) > 0 for X in self.train_X_list):
    #         return

    #     pipeline = self.opt_form["opt"]["pipeline"]
    #     strategy_dict = pipeline["strategy"]
    #     strategy_cls = strategy_dict["cls"]
    #     strategy_params = strategy_dict.get("params", {})

    #     self.strategy = strategy_cls()
    #     self.model = self.strategy.build_model(
    #         self.train_X_list,
    #         self.train_Y_list,
    #         self.bounds,
    #         **strategy_params,
    #     )