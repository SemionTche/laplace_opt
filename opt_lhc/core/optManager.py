# libraries
from typing import Optional
import pathlib
import torch
import h5py
from PyQt6.QtCore import pyqtSignal, QObject

from server_lhc.serverLHC import ServerLHC
from server_lhc.protocol import DEVICE_OPT
from server_lhc.serverController import ServerController

# project
from core.optimizer import Optimizer
from core.dataWatcher import DataWatcher
from core.modelSaver import ModelSaver
from utils.save_configuration import save_config

class OptManager(QObject):

    on_server_address = pyqtSignal(str)     # is_on and server_address

    def __init__(self):
        super().__init__() # heritage from QObject

        # controller to emit signals from server
        self.server_controller = ServerController()

        self.optimizer: Optional[Optimizer] = None
        self.model_config = None
        self.bounds = None

        self.train_X = None
        self.train_Y = None

        self.data_file: Optional[pathlib.Path] = None
        self.last_size = 0
        self.watcher: Optional[DataWatcher] = None

        self.model_saver = None
        self.step = 0

        self.is_saving = False
        self._opt_form = {}
        self.is_online = False
    
    @property
    def opt_form(self) -> dict:
        return self._opt_form

    def init_process(self, opt_form: dict) -> None:
        self.is_online = opt_form["exec"]["is_online"]
        self.set_form(opt_form)
        self.init_opt()

    def set_form(self, opt_form: dict) -> None:
        self._opt_form = opt_form
        self.is_saving = save_config(opt_form)

    def init_opt(self) -> None:
        self.bounds = self.get_boundaries()
        init = self.opt_form["init"]
        init_cls, params = init.values()
        self.init_x = init_cls.generate(bounds = self.bounds, **params)

        print(self.init_x)

        data = {
            "is_init": True,
            "is_opt": False,
            "data": self.init_x.tolist()
        }
        
        if self.is_online:
            self.serv.set_data(data)
        # Doesn't work for q = 1
        # making the string with sobol proposal to sent it to log.
        # sobol_candidate = []
        # for i in range(init_x.shape[0]):
        #     batch_lines = [f"Sobol batch {i + 1}:"]
        #     for j in range(init_x.shape[1]):
        #         coords = ", ".join(f"{init_x[i, j, k].item()}" for k in range(self.bounds.shape[-1]))
        #         batch_lines.append(f"  Candidate {j + 1}: {coords}")
        #     sobol_candidate.append("\n".join(batch_lines))
        
        # print("Sobol suggestion:\n", "\n\n".join(sobol_candidate)) # for logs add %s after first \n


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
            
            self.serv.start() # start the server

            # emit a signal to transmit the server address to the ExecutionPanel
            self.on_server_address.emit(self.serv.address_for_client)
        
        else: # if off
            self.serv.stop() # stop the server


    def get_boundaries(self) -> torch.Tensor:
        bounds = []
        if self.opt_form:
            inputs = self.opt_form["inputs"]
        
        for name, cls in inputs.items():
            bounds.append(cls.bounds)
        
        return torch.Tensor(bounds).T # tensor must be 2 x d



    # ---------- configuration ----------
    def configure_model(self, model_config: dict, bounds: torch.Tensor):
        self.model_config = model_config
        self.bounds = bounds

        if not model_config["enabled"]:
            self.optimizer = None
            return

        self.optimizer = Optimizer(
            bounds=bounds,
            classes=model_config["classes"],
            hyperparameters=model_config["hyperparameters"],
        )

    def configure_data_source(self, folder: pathlib.Path, parent=None):
        self.data_file = folder / "measurements.hdf5"

        if not self.data_file.exists():
            raise FileNotFoundError(self.data_file)

        self.watcher = DataWatcher(folder, parent=parent)
        self.watcher.new_data_available.connect(self.on_new_data_available)

    # ---------- data handling ----------
    def on_new_data_available(self):
        X, Y = self._read_hdf5()

        if self.train_X is None:
            self.initialize(X, Y)
        else:
            if X.shape[0] > self.last_size:
                X_new = X[self.last_size:]
                Y_new = Y[self.last_size:]
                self.add_data(X_new, Y_new)

        self.last_size = X.shape[0]

        if self.optimizer is None:
            return

        q = self.model_config.get("q", 1)
        X_next = self.get_next_candidates(q)

        self.step += 1

        if self.model_saver:
            self.model_saver.save(
                train_X=self.train_X,
                train_Y=self.train_Y,
                next_candidates=X_next,
                step=self.step,
                model_config=self.model_config,
            )


    def _read_hdf5(self):
        with h5py.File(self.data_file, "r") as f:
            X = torch.tensor(f["positions"][:], dtype=torch.float32)
            Y = torch.tensor(f["values"][:], dtype=torch.float32)
        return X, Y

    # ---------- initialization ----------
    def initialize(self, X_init: torch.Tensor, Y_init: torch.Tensor):
        self.train_X = X_init
        self.train_Y = Y_init

        if self.optimizer is not None:
            self.optimizer.initialize(X_init, Y_init)

    # ---------- data updates ----------
    def add_data(self, X_new: torch.Tensor, Y_new: torch.Tensor):
        self.train_X = torch.cat([self.train_X, X_new], dim=0)
        self.train_Y = torch.cat([self.train_Y, Y_new], dim=0)

        if self.optimizer is not None:
            self.optimizer.update_data(X_new, Y_new)
    
    def configure_model_saving(self, folder: pathlib.Path):
        self.model_saver = ModelSaver(folder)


    # ---------- optimization ----------
    def get_next_candidates(self, q: int):
        if self.optimizer is None:
            raise RuntimeError("Optimizer not enabled")
        return self.optimizer.get_next_candidates(q)
