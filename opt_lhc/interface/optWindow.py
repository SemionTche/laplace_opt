# libraries
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QMessageBox, QPushButton, QGroupBox
)
from PyQt6.QtGui import QIcon

import qdarkstyle
import pathlib

# project
from interface.executionPanel import ExecutionPanel
from interface.rowPanel import RowPanel
from interface.inputRow import InputRow
from interface.objectiveRow import ObjectiveRow

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

        # Server and reader mode
        self.execution_panel = ExecutionPanel()
        main_layout.addWidget(self.execution_panel)

        # --- Block 2: Inputs ---
        self.input_panel = RowPanel(
            title="Available Inputs",
            row_class=InputRow,
            get_classes_type="inputs"
        )

        # --- Block 3: Objectives ---
        self.objective_panel = RowPanel(
            title="Available Objectives",
            row_class=ObjectiveRow,
            get_classes_type="objectives"
        )
        
        self.input_rows = self.input_panel.get_rows()
        self.objective_rows = self.objective_panel.get_rows()  # dict[str, ObjectiveRow]

        # input / obj layout
        middle_layout = QHBoxLayout()
        middle_layout.addWidget(self.input_panel, stretch=3)
        middle_layout.addWidget(self.objective_panel, stretch=2)
        main_layout.addLayout(middle_layout)

        # Placeholders
        init_panel = QGroupBox("Initialization")
        init_layout = QVBoxLayout(init_panel)
        init_layout.addWidget(QLabel("Placeholder for initialization settings (Sobol, file, no init?)"))

        model_panel = QGroupBox("Model")
        model_layout = QVBoxLayout(model_panel)
        model_layout.addWidget(QLabel("Placeholder for model settings (gridScan, qNEHVI)"))

        # Layout for the placeholders
        bottom_panels_layout = QHBoxLayout()
        bottom_panels_layout.addWidget(init_panel, stretch=1)
        bottom_panels_layout.addWidget(model_panel, stretch=1)

        main_layout.addLayout(bottom_panels_layout)


        # --- Bottom: Validate and Create Button ---
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        self.validate_btn = QPushButton("Validate and Create")
        # self.validate_btn.clicked.connect(self.on_validate)
        bottom_layout.addWidget(self.validate_btn)

        main_layout.addLayout(bottom_layout)

        self.server_controller = ServerController()

        self.actions()

        
    
    def actions(self):
        self.execution_panel.server_state_changed.connect(
            self.server_launch
        )
        
        self.server_controller.saving_path_changed.connect(
            self.execution_panel.saving_entry.setText
        )
    
    def server_launch(self, server_state: bool) -> None:
        if server_state:
            self.serv = ServerLHC(name="Optimization", 
                                  address="tcp://*:1254", 
                                  freedom=0, 
                                  device=DEVICE_OPT,
                                  data={})
            # bridge server -> controller
            self.serv.on_saving_path_changed = (
                self.server_controller.on_server_save_path
            )
            self.serv.start()
            self.execution_panel.set_server_address(self.serv.address_for_client)
        else:
            self.serv.stop()
    
    def closeEvent(self, event) -> None:
        '''
        Function called when the window is closing.
        Close every client of client manager.
        '''
        if self.execution_panel.is_online_enabled():
            self.serv.stop()
        event.accept()
    
    