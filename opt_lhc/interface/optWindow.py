# libraries
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QMessageBox
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

from utils.model_form import make_form, ValidationLevel


class OptWindow(QMainWindow):
    
    def __init__(self):

        super().__init__() # heritage from QMainWindow

        self.opt_manager = OptManager()
        
        self.set_up()  # build the window panels and buttons

        self.actions() # defines the actions of the window

    def set_up(self) -> None:
        '''
        Build the panels and buttons of the main opt window.
        '''        
        p = pathlib.Path(__file__) # path to the current file
        
        # set title, geometry and style
        self.setWindowTitle("Optimization Window")
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        self.setGeometry(100, 30, 1000, 700)

        # icon
        icon_path = p.parent / 'icons' # path to the icon folder
        self.setWindowIcon( QIcon( str(icon_path / 'LOA.png') ) )

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

            # input / obj layout
        middle_layout = QHBoxLayout()
        middle_layout.addWidget(self.input_panel, stretch=3)
        middle_layout.addWidget(self.objective_panel, stretch=2)
        main_layout.addLayout(middle_layout)

        # Block 3: Init
        self.init_panel = InitializationPanel()
        main_layout.addWidget(self.init_panel, stretch=1)

        # Block 4: Pipeline
        self.opt_panel = OptPanel()
        main_layout.addWidget(self.opt_panel, stretch=1)

        # Block 5: Start and Stop buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
            # Stop
        self.stop_button = QPushButton("Stop")
        self.stop_button.setFixedWidth(120)
        bottom_layout.addWidget(self.stop_button)
            # Start
        self.start_button = QPushButton("Start")
        self.start_button.setFixedWidth(120)
        bottom_layout.addWidget(self.start_button)

        main_layout.addLayout(bottom_layout)

    
    def actions(self) -> None:
        '''
        Defines the actions between the several panels and
        make the bridget with the optimization manager.
        '''
        # Start and Stop buttons
        self.start_button.clicked.connect(self.on_start)
        self.stop_button.clicked.connect(self.on_stop)

        # turn on / off the server according to the server signal
        self.execution_panel.server_state_changed.connect(
            self.opt_manager.server_launch
        )

        # enable / disable input addresses with respect to the server signal
        self.execution_panel.server_state_changed.connect(
            self.input_panel.enable_addresses
        )
        
        # change the saving path when the server get the "SAVE" cmd
        self.opt_manager.server_controller.saving_path_changed.connect(
            self.execution_panel.set_path_saving
        )

        # transmit the server address from the server to the ExecutionPanel
        self.opt_manager.on_server_address.connect(
            self.execution_panel.set_server_address
        )
    
    def on_start(self) -> None:
        execution = self.execution_panel.get_execution()
        inputs = self.input_panel.get_enabled_rows()
        objectives = self.objective_panel.get_enabled_rows()
        init = self.init_panel.get_initialization()
        opt = self.opt_panel.get_opt()

        form, (level, message) = make_form(
            exec=execution,
            inputs=inputs,
            obj=objectives,
            init=init,
            opt=opt
        )

        if level == ValidationLevel.ERROR:
            QMessageBox.critical(
                self,
                "Invalid configuration",
                message
            )
            return
        
        if level == ValidationLevel.WARNING:
            reply = QMessageBox.warning(
                self,
                "Configuration warning",
                message + "\n\nDo you want to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
            
        print("Starting optimization with form:")
        print(form)
        self.execution_panel.set_locked(True)
        self.opt_manager.init_process(form)


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
            self.opt_manager.serv.stop()
        event.accept()