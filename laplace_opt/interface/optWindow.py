# libraries
import pathlib

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QMessageBox, QLabel
)
from PyQt6.QtGui import QIcon
import qdarkstyle
from laplace_log import log

# project
from .panels import (
    ExecutionPanel, InOutPanel,
    InitializationPanel, OptPanel
)
from ..core.optManager import OptManager
from ..utils.model_form import make_form, ValidationLevel
from ..utils.json_encoder import json_style


class OptWindow(QMainWindow):
    
    def __init__(self):

        super().__init__() # heritage from QMainWindow

        self.opt_manager = OptManager()  # class managing the optimization
        
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
        self.setGeometry(100, 30, 1200, 700)

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
        self.input_panel = InOutPanel(folder_name="inputs")

        # Block 2: Objectives
        self.objective_panel = InOutPanel(folder_name="objectives")

            # input / obj layout
        in_out_layout = QHBoxLayout()
        in_out_layout.addWidget(self.input_panel, stretch=1)
        in_out_layout.addWidget(self.objective_panel, stretch=1)
        main_layout.addLayout(in_out_layout)

        # Block 3: Init
        self.init_panel = InitializationPanel()
        main_layout.addWidget(self.init_panel, stretch=1)

        # Block 4: Pipeline
        self.opt_panel = OptPanel()
        main_layout.addWidget(self.opt_panel, stretch=1)

        # Block 5: Start and Stop buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
            # state label
        self.status_label = QLabel("🟢 Ready")
        self.status_label.setStyleSheet("font-weight: bold;")
        bottom_layout.addWidget(self.status_label)
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

        # turn on / off the server according to the ExecutionPanel checkbox
        self.execution_panel.server_state_changed.connect(
            self.opt_manager.server_launch
        )

        # enable / disable input addresses with respect to the ExecutionPanel checkbox
        self.execution_panel.server_state_changed.connect(
            self.input_panel.enable_ip_port
        )
        # enable / disable objective addresses with respect to the ExecutionPanel checkbox
        self.execution_panel.server_state_changed.connect(
            self.objective_panel.enable_ip_port
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
        '''
        Function used when 'start_button' is pressed. Create a 
        config dictionary gathering the panel informations and 
        transmit it to the optimization manager.

        Check if the panel informations are sufficient to continue,
        raise error and warning message box if needed.
        '''
        log.debug("Start button pressed.")

        # gather the panel informations
        execution = self.execution_panel.get_execution()
        inputs = self.input_panel.get_enabled_rows()
        objectives = self.objective_panel.get_enabled_rows()
        init = self.init_panel.get_initialization()
        opt = self.opt_panel.get_opt()

        # make the config dictionary
        form, (level, message) = make_form(
            exec=execution,
            inputs=inputs,
            obj=objectives,
            init=init,
            opt=opt
        )

        # if there is an error
        if level == ValidationLevel.ERROR:
            # make an error message box
            QMessageBox.critical(self, "Invalid configuration", message)
            log.error(f"Invalid configuration: {message}")
            return
        
        # elif there is a warning
        elif level == ValidationLevel.WARNING:
            # make a warning message box
            reply = QMessageBox.warning(
                self,
                "Configuration warning",
                message + "\n\nDo you want to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            # let the user decide to continue or quit
            if reply == QMessageBox.StandardButton.No:
                log.warning(f"{message} Answer: canceled.")
                return
            log.warning(f"{message} Answer: continue.")

        log.info("Starting optimization with form:\n" + json_style(form))
        self.set_opt_state(True)
        self.opt_manager.init_process(form)    # send the config dictionary to the optimization manager


    def on_stop(self):
        '''
        Function used when 'stop_button' is pressed.
        '''
        log.debug("Stop button pressed.")

        self.opt_manager.stop_opt()

        self.set_opt_state(False)
        pass

    
    def set_opt_state(self, optimizing: bool):
        if optimizing:
            self.status_label.setText("🟡 Optimizing...")
            self.status_label.setStyleSheet("color: orange; font-weight: bold;")
            self.start_button.setEnabled(False)      # lock the start button
            self.execution_panel.set_locked(True)    # lock the ExecutionPanel
        else:
            self.status_label.setText("🟢 Ready")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.start_button.setEnabled(True)      # unlock the start button
            self.execution_panel.set_locked(False)  # unlock the ExecutionPanel


    def closeEvent(self, event) -> None:
        '''
        Function called when the window is closing.
        
        Close the server stored in 'OptManager'.
        '''
        if self.execution_panel.is_online_enabled():
            self.opt_manager.server_launch(server_state=False)
        event.accept()