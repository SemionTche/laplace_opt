# libraries
from PyQt6.QtCore import pyqtSignal, QObject

from laplace_server.server_lhc import ServerLHC
from laplace_server.protocol import DEVICE_OPT
from laplace_server.server_controller import ServerController

from laplace_log import log

# project
from ..core.optimizer import Optimizer
from ..utils.save_form import save_opt_form
from ..utils.config_helper import get_from_config


class OptManager(QObject):
    '''
    High-level manager coordinating optimization, server, and UI signals.

    Handles optimizer lifecycle, server communication, and optimization state.
    '''

    on_server_address = pyqtSignal(str)  # transmit the optimizer server address
    data_for_plot = pyqtSignal(list)

    def __init__(self):
        '''
        Initialize the optimization manager.

        Sets up controller objects and internal state flags.
        '''
        super().__init__() # heritage from QObject

        # controller class to emit signals from server
        self.server_controller = ServerController()

        self.is_saving: bool = False
        self.is_online: bool = False
        self.is_opt: bool = False
        self._opt_form = {}

    @property
    def opt_form(self) -> dict:
        '''Property to prevent 'opt_form' modifications.'''
        return self._opt_form


    def init_process(self, opt_form: dict) -> None:
        '''
        Initialize and start an optimization process.
        
        Creates the optimizer, configures server connections if online,
        and requests the first batch of candidates.

            Arg:
                opt_form: (dict)
                    the optimization dictionary required to
                    start an initialization or an optimization.
        '''
        self.set_form(opt_form)  # set and save the opt_form

        self.optimizer = Optimizer(self.opt_form)  # make an optimizer drived by this form

        self.is_online = self.opt_form["exec"]["is_online"]  # is it an online process
        self.is_opt = self.opt_form["opt"]["enabled"]        # is there an optimization
        
        if self.is_online: # if dealing with a server

            # when the server receives a CMD_OPT, update the optimizer
            self.server_controller.opt_received.connect(
                self.optimizer.update_opt
            )

            # when the server receives a CMD_OPT, transmit it to the plot window
            self.server_controller.opt_received.connect(
                self._handle_new_result
            )

            # when new candidates are provided by optimizer, update the server payload
            self.optimizer.new_candidates.connect(
                self.serv.set_data
            )

        self.optimizer.init_opt()   # get the first candidates


    def _handle_new_result(self, data) -> None:
        results = data.get("results", [])
        self.data_for_plot.emit(results)


    def stop_opt(self) -> None:
        '''Stop the optimization process.'''
        
        if self.is_online:  # if the server is involved

            # disconnect the relevant features
            self.server_controller.opt_received.disconnect()
            self.optimizer.new_candidates.disconnect()

        self.optimizer.save_end()

        # reset the checkers
        self.is_online = False
        self.is_opt = False
        self.is_saving = False
        log.info("Optimization stopped.")


    def server_launch(self, server_state: bool) -> None:
        '''
        Start or stop the optimization server.
        
            Args:
                server_state: (bool) 
                    True to start the server, False to stop it.
        '''
        if server_state: # if on
            
            # get the server port
            port = get_from_config(
                module="server", 
                item="port", 
                default_value="7531", 
                type=str
            )
            
            # create the server
            self.serv = ServerLHC(
                name="Optimization", 
                address=f"tcp://*:{port}", 
                freedom=0, 
                device=DEVICE_OPT,
                data={},
                empty_data_after_get=True
            )

            # define the functions used by the server on specific messages
                
                # when the CMD_SAVE is received, emit a signal to change the saving path
            self.serv.set_on_saving_path_changed(
                self.server_controller.on_saving_path_changed
            )
                # when CMD_OPT is received, emit signal to update the optimizer
            self.serv.set_on_opt(
                self.server_controller.on_opt
            )

            self.serv.start() # start the server

            # emit a signal to transmit the server address to the ExecutionPanel
            self.on_server_address.emit(f"{self.serv.server_ip}:{self.serv.server_port}")
        
        else:                # else means server off
            self.serv.stop() # stop the server
            log.info("Server stopped.")


    ### helpers
    def set_form(self, opt_form: dict) -> None:
        '''Helper setting and saving the 'opt_form' dictionary.'''
        self._opt_form = opt_form                 # set the attribute
        self.is_saving = save_opt_form(opt_form)  # save the configuration