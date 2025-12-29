# libraries
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton
)
from PyQt6.QtGui import QIcon

import qdarkstyle
import pathlib
import torch

# project
from interface.executionPanel import ExecutionPanel
from interface.inOutPanel import InOutPanel
from interface.initializationPanel import InitializationPanel
from interface.optPanel import OptPanel

from core.optManager import OptManager

from server_lhc.serverLHC import ServerLHC
from server_lhc.protocol import DEVICE_OPT
from server_lhc.serverController import ServerController


class OptWindow(QMainWindow):
    
    def __init__(self):

        super().__init__() # heritage from QMainWindow

        # Set window title
        self.setWindowTitle("Optimization Window")
        p = pathlib.Path(__file__)
        icon_path = p.parent / 'icons'
        
        # icon, style and geometry
        self.setWindowIcon( QIcon( str(icon_path / 'LOA.png') ) )
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        self.setGeometry(100, 30, 1000, 700)

        # central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Block 1: Server and Reader modes
        self.execution_panel = ExecutionPanel()
        main_layout.addWidget(self.execution_panel)

        # Block 2: Inputs
        self.input_panel = InOutPanel(
            title="Available Inputs",
            folder_name="inputs"
        )

        # Block 2: Objectives
        self.objective_panel = InOutPanel(
            title="Available Objectives",
            folder_name="objectives"
        )
            # helpers input / obj rows
        self.input_rows = self.input_panel.get_rows()
        self.objective_rows = self.objective_panel.get_rows()  # dict[str, ObjectiveWidget]

            # input / obj layout
        middle_layout = QHBoxLayout()
        middle_layout.addWidget(self.input_panel, stretch=3)
        middle_layout.addWidget(self.objective_panel, stretch=2)
        main_layout.addLayout(middle_layout)

        # Block 3: Init
        self.init_panel = InitializationPanel()
        main_layout.addWidget(self.init_panel, stretch=1)

        # Block 4: Pipeline
        self.model_panel = OptPanel()
        main_layout.addWidget(self.model_panel, stretch=1)

        # Block 5: Start and Stop buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        self.stop_button = QPushButton("Stop")
        bottom_layout.addWidget(self.stop_button)
        
        self.start_button = QPushButton("Start")
        bottom_layout.addWidget(self.start_button)

        main_layout.addLayout(bottom_layout)

        # controller to emit signals from server
        self.server_controller = ServerController()

        self.actions() # defines the actions of the window

    
    def actions(self):
        # Start and Stop buttons
        self.start_button.clicked.connect(self.on_start)
        self.stop_button.clicked.connect(self.on_stop)

        # turn on / off the server according to the server signal
        self.execution_panel.server_state_changed.connect(
            self.server_launch
        )

        self.execution_panel.server_state_changed.connect(
            self.input_panel.enable_addresses
        )
        
        # change the saving path when the server get the "SAVE" cmd
        self.server_controller.saving_path_changed.connect(
            self.execution_panel.saving_entry.setText
        )
    

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
            
            # bridge server -> controller (to emit signal when the saving path is changing)
            self.serv.on_saving_path_changed = (
                self.server_controller.on_server_save_path
            )
            
            self.serv.start() # start the server
            # update the address in execution panel
            self.execution_panel.set_server_address(self.serv.address_for_client)
        
        else: # if off
            self.serv.stop() # stop the server
    
    def on_start(self):
        # bounds
        bounds = self.get_bounds_from_inputs()

        # model config
        model_cfg = self.model_panel.get_config()

        # data path
        data_path = pathlib.Path(
            self.execution_panel.saving_entry.text()
        )

        self.opt_manager = OptManager()
        self.opt_manager.configure_model(model_cfg, bounds)

        if data_path.exists():
            self.opt_manager.configure_data_source(
                data_path,
                parent=self  # important for Qt ownership
            )

    def on_stop(self):
        pass

    def get_bounds_from_inputs(self) -> torch.Tensor:
        bounds = []

        for row in self.input_panel.get_rows().values():
            if row.is_enabled():
                value = row.get_value()
                if value is None:
                    raise ValueError(f"Invalid bounds for input '{row.name}'")
                bounds.append(value)

        if not bounds:
            raise RuntimeError("No inputs enabled")

        # shape: [2, D] → torch format expected by BO libs
        bounds = torch.tensor(bounds, dtype=torch.float32).T
        return bounds

    
    def closeEvent(self, event) -> None:
        '''
        Function called when the window is closing.
        Close every client of client manager.
        '''
        if self.execution_panel.is_online_enabled():
            self.serv.stop()
        event.accept()
    
    