# libraries
import torch
from PyQt6.QtCore import pyqtSignal, QObject

from server_lhc.serverLHC import ServerLHC
from server_lhc.protocol import DEVICE_OPT
from server_lhc.serverController import ServerController

# project
from utils.save_configuration import save_config

class OptManager(QObject):

    on_server_address = pyqtSignal(str)     # is_on and server_address

    def __init__(self):
        super().__init__() # heritage from QObject

        # controller to emit signals from server
        self.server_controller = ServerController()

        self.is_saving = False
        self.is_online = False
        self.is_opt = False
        self._opt_form = {}

        self.strategy = None
        self.model = None
        self.train_X_list = None
        self.train_Y_list = None

        self.server_controller.get_received.connect(
            self.empty_data
        )

        self.server_controller.opt_received.connect(
            self.update_opt
        )
    

    @property
    def opt_form(self) -> dict:
        '''Property to prevent 'opt_form' modifications.'''
        return self._opt_form


    def init_process(self, opt_form: dict) -> None:
        '''
        Function used to inialize the 'OptManager' class.
        The server part is handled separatly.

            Arg:
                opt_form: (dict)
                    the optimization dictionary required to
                    start an initialization or an optimization.
        '''
        self.is_online = opt_form["exec"]["is_online"]  # whether the optimization is accessible from the server
        self.is_opt = opt_form["opt"]["enabled"]
        self.set_form(opt_form)                         # set the opt_form as attribut of the class
        self.init_opt()                                 # make initialization process
        
        if self.is_opt:
            self.pipeline = self.opt_form["opt"]["pipeline"]


    def set_form(self, opt_form: dict) -> None:
        '''Helper that set and save the 'opt_form' dictionary of the optimization.'''
        self._opt_form = opt_form     # set the attribute
        self.is_saving = save_config(opt_form)  # save the configuration


    def init_opt(self) -> None:
        '''
        Use the initialization refered in the 'opt_form' dictrionary.
        '''
        self.bounds_dict, self.bounds = self.get_boundaries() # get the boundaries from the input dictionary
        init = self.opt_form["init"]                          # get the init dictionary
        init_cls, params = init.values()                      # get the class to use and its parameters
        init_cls = init_cls()                                 # create an instance of the class
        self.init_x = init_cls.generate(bounds=self.bounds, **params)  # generate the first points to sample

        data = self.build_data_payload(                       # make the payload for the server
            self.init_x,
            self.bounds_dict,
            is_init=True,
            is_opt=False,
        )
        
        if self.is_online:
            self.serv.set_data(data)                          # add the payload to the server

        print("Sobol suggestion:\n", self.format_print(self.init_x, self.bounds_dict)) # print the sample candidates


    def get_boundaries(self) -> tuple[dict[str, tuple], torch.Tensor]:
        '''
        Helper that extract the boundaries from the 'input' dictionary
        stored in the optimization form.
        
        Return both a dictionary where the boundaries and address of the
        input are stored using there names and a 'Torch.Tensor' to gather
        the boundaries.
        '''
        bounds = []        # gather the boundaries
        bounds_dict = {}   # information about the inputs
        
        inputs = self.opt_form["inputs"]  # get the input dictionary from the form
        
        for name, cls in inputs.items():  # for each element
            bounds.append(cls.bounds)     # add the boundaries in the list
            bounds_dict[name] = {"address": cls.address, "bounds": cls.bounds} # create the field to gather the address and the boundaries
        
        bounds = torch.Tensor(bounds).T   # convert the list to a tensor. The tensor must be 2 x d (d = input dimension)
        
        return bounds_dict, bounds


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

    

    def format_print(self, X: torch.Tensor, bounds_dict: dict) -> str:
        '''
        Print the values that each input should take. Use a X 'torch.Tensor'
        for the values and a 'bounds_dict' for the input addresses.
        '''
        addresses = [v["address"] for v in bounds_dict.values()]  # make a list of addresses

        lines = []
        for i in range(X.shape[0]):                            # for each sample
            lines.append(f"batch {i + 1}:")                     # print which sample it is
            for j in range(X.shape[1]):                          # for each candidate
                coords = ", ".join(
                    f"{addr}={X[i, j, k].item():.6g}"            # for each input, address = value
                    for k, addr in enumerate(addresses)
                )
                lines.append(f"  Candidate {j + 1}: {coords}")   # print the candidate
        
        return "\n".join(lines)


    def server_launch(self, server_state: bool) -> None:
        '''
        Function made to turn on / off the OPT server according
        to the state given in argument.
        '''
        if server_state: # if on
            
            # create the server
            self.serv = ServerLHC(name="Optimization", 
                                  address="tcp://*:1254", 
                                  freedom=0, 
                                  device=DEVICE_OPT,
                                  data={})
            
            # bridge server -> controller (to emit signal when the saving path is changed)
            self.serv.set_on_saving_path_changed(
                self.server_controller.on_server_save_path
            )
            
            self.serv.set_on_get(
                self.server_controller.on_get
            )

            self.serv.set_on_opt(
                self.server_controller.on_opt
            )

            self.serv.start() # start the server

            # emit a signal to transmit the server address to the ExecutionPanel
            self.on_server_address.emit(self.serv.address_for_client)
        
        else: # if off
            self.serv.stop() # stop the server

    def update_opt(self, data: dict) -> None:
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
                dtype=torch.float32,
            )

            for obj_idx, y_val in enumerate(r["output"]):
                if y_val is None:
                    continue

                self.train_X_list[obj_idx].append(x)
                self.train_Y_list[obj_idx].append(
                    torch.tensor([y_val], dtype=torch.float32)
                )

        # Convert lists → tensors
        for i in range(len(self.train_X_list)):
            if len(self.train_X_list[i]) == 0:
                continue

            self.train_X_list[i] = torch.stack(self.train_X_list[i], dim=0)
            self.train_Y_list[i] = torch.stack(self.train_Y_list[i], dim=0)

        print("[OPT] train_X_list status:")
        for i, X in enumerate(self.train_X_list):
            print(f"  train_X_list[{i}] = {X}")
            # if isinstance(X, list):
            #     print(f"  obj {i}: list with {len(X)} entries")
            # else:
            #     print(f"  obj {i}: tensor shape {tuple(X.shape)}")

        print("[OPT] train_Y_list status:")
        for i, Y in enumerate(self.train_Y_list):
            print(f"  train_Y_list[{i}] = {Y}")
            # if isinstance(Y, list):
            #     print(f"  obj {i}: list with {len(Y)} entries")
            # else:
            #     print(f"  obj {i}: tensor shape {tuple(Y.shape)}")


        self.build_strategy_model()



    def build_strategy_model(self) -> None:
        """
        Instantiate the optimization strategy and build its model
        using the current training data.
        """
        if not self.is_opt:
            return

        if self.train_X_list is None or self.train_Y_list is None:
            return

        # Require at least one objective with data
        if not any(len(X) > 0 for X in self.train_X_list):
            return

        pipeline = self.opt_form["opt"]["pipeline"]
        strategy_dict = pipeline["strategy"]
        strategy_cls = strategy_dict["cls"]
        strategy_params = strategy_dict.get("params", {})

        self.strategy = strategy_cls()
        self.model = self.strategy.build_model(
            self.train_X_list,
            self.train_Y_list,
            self.bounds,
            **strategy_params,
        )

    def empty_data(self) -> None:
        self.serv.set_data({})