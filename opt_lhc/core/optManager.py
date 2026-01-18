# libraries
from PyQt6.QtCore import pyqtSignal, QObject

from server_lhc.serverLHC import ServerLHC
from server_lhc.protocol import DEVICE_OPT
from server_lhc.serverController import ServerController

from log_laplace.log_lhc import log

# project
from core.optimizer import Optimizer

from utils.save_configuration import save_config


class OptManager(QObject):

    on_server_address = pyqtSignal(str)     # is_on and server_address

    def __init__(self):
        super().__init__() # heritage from QObject

        # controller class to emit signals from server
        self.server_controller = ServerController()

        self.is_saving: bool = False
        self.is_online: bool = False
        self.is_opt: bool = False
        self.is_runing: bool = False
        self._opt_form = {}

        self.strategy = None
        self.model = None
        self.train_X_list = None
        self.train_Y_list = None


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
        self.set_form(opt_form)  # set and save the opt_form

        self.optimizer = Optimizer(self.opt_form)  # make an optimizer drived by this form

        self.is_online = self.opt_form["exec"]["is_online"]  # is it an online init + optimization
        self.is_opt = self.opt_form["opt"]["enabled"]        # is there an optimization
        
        if self.opt_form["exec"]["saving_path"]:             # is the model saved
            self.is_saving = True

        if self.is_online:

            # when the server received an CMD_OPT, update the optimizer
            self.server_controller.opt_received.connect(
                self.optimizer.update_opt
            )

            # when new candidates are provided, update the server payload
            self.optimizer.new_candidates.connect(
                self.up_serv_temp
            )

        self.optimizer.init_opt()   # get the first candidates


    def stop_opt(self):

        if self.is_online:
            self.server_controller.opt_received.disconnect()

            self.optimizer.new_candidates.disconnect()

        self.is_runing = False
        self.is_online = False
        self.is_opt = False
        self.is_saving = False


    def up_serv_temp(self, data: dict):
        print("here we are on business")
        self.serv.set_data(data)
        print(f"serv data update = {self.serv.data}")


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
                                  data={},
                                  empty_data_after_get=True)
            
            # bridge server -> controller (to emit signal when the saving path is changed)
            self.serv.set_on_saving_path_changed(
                self.server_controller.on_server_save_path
            )

            self.serv.set_on_opt(
                self.server_controller.on_opt
            )

            self.serv.start() # start the server

            # emit a signal to transmit the server address to the ExecutionPanel
            self.on_server_address.emit(self.serv.address_for_client)
        
        else: # if off
            self.serv.stop() # stop the server


    ### helpers

    def set_form(self, opt_form: dict) -> None:
        '''Helper setting and saving the 'opt_form' dictionary.'''
        self._opt_form = opt_form               # set the attribute
        self.is_saving = save_config(opt_form)  # save the configuration