# libraries
import torch
from PyQt6.QtCore import pyqtSignal, QObject

from server_lhc.serverLHC import ServerLHC
from server_lhc.protocol import DEVICE_OPT
from server_lhc.serverController import ServerController

# project
from core.optimizer import Optimizer
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
        self.set_form(opt_form)                         # set the opt_form as attribut of the class
        
        self.optimizer = Optimizer(self.opt_form)
        
        self.is_online = self.opt_form["exec"]["is_online"]  # whether the optimization is accessible from the server
        self.is_opt = self.opt_form["opt"]["enabled"]
        data = self.optimizer.init_opt()
        print(f"[Data set to server] data = {data}")
        
        if self.is_online:
            self.serv.set_data(data)                 # add the payload to the server

            self.server_controller.opt_received.connect(
                self.optimizer.update_opt
            )

            self.optimizer.new_candidates.connect(
                self.up_serv_temp
            )
    
    def up_serv_temp(self, data: dict):
        print("here we are on business")
        self.serv.set_data(data)
        print(f"serv data update = {self.serv.data}")

    # def print_test(data: dict):
    #     print(f"test passed {data}")

    def set_form(self, opt_form: dict) -> None:
        '''Helper that set and save the 'opt_form' dictionary of the optimization.'''
        self._opt_form = opt_form     # set the attribute
        self.is_saving = save_config(opt_form)  # save the configuration


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

    
    def empty_data(self) -> None:
        if self.serv.reset_data:
            self.serv.set_data({})
            print("server is empty")