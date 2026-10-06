# libraries
from laplace_log import log
from PyQt6.QtWidgets import (
    QGroupBox, QGridLayout, QRadioButton,
    QCheckBox, QLineEdit, QPushButton,
    QLabel, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal

# project
from ...utils.config_helper import (
    get_from_config, set_in_config
)
from ...utils.model_source import ModelSource


class ExecutionPanel(QGroupBox):
    '''
    Panel handling execution mode and data source configuration.
    
    A lock button allows to enable / disable every widget.
    '''
    # signal indicating that the server checkbox state changed
    server_state_changed = pyqtSignal(bool)

    def __init__(self, source: ModelSource):
        ''' 
        Arg:
            source (ModelSource):
                Object storing the 'model_construction' folder 
                location from which the structure is loaded.
        '''
        super().__init__("Execution & Data Configuration")
        self.source = source
        self.set_up()           # build the elements
        self.actions()          # defines the panel actions


    def set_up(self) -> None:
        '''
        Function made to create and set 
        the elements of the ExecutionPanel.
        '''
        exc_layout = QGridLayout(self)

        # Online execution
        self.server_checkbox = QCheckBox("Run online (start server)")
        self.server_entry = QLineEdit("")  # indicates the optimization server address
        self.server_entry.setReadOnly(True)

        # Model entry
        self.model_path_entry = QLineEdit()
        self.model_path_entry.setPlaceholderText("model path")
        self.model_browse_button = QPushButton("Model Browse")

        # Saving entry
        self.saving_entry = QLineEdit()
        self.saving_entry.setPlaceholderText("saving path")
        self.save_browse_button = QPushButton("Save Browse")

        # Lock
        self.lock_button = QPushButton("🔒 Lock configuration")
        self.lock_button.setCheckable(True)

        # exc_layout
        exc_layout.addWidget(self.server_checkbox, 0, 0)
        exc_layout.addWidget(QLabel("Server address:"), 0, 1)
        exc_layout.addWidget(self.server_entry, 0, 2)

        exc_layout.addWidget(QLabel("Model path:"), 1, 1)
        exc_layout.addWidget(self.model_path_entry, 1, 2)
        exc_layout.addWidget(self.model_browse_button, 1, 3)

        exc_layout.addWidget(QLabel("Saving path:"), 2, 1)
        exc_layout.addWidget(self.saving_entry, 2, 2)
        exc_layout.addWidget(self.save_browse_button, 2, 3)

        exc_layout.addWidget(self.lock_button, 0, 3, alignment=Qt.AlignmentFlag.AlignRight)

        exc_layout.setColumnStretch(2, 1) # set the Stretch of the 2nd column, to 1 (other are 0)

        # get the default execution (model and saving) path
            # get and set default saving path
        self.save_path = get_from_config(
            module="interface",
            item="saving_path",
            default_value="",
            type=str
        )
        self.set_path_saving(self.save_path)  # path update when the panel is unlocked
        
            # get and set default model path
        self.set_path_model( str(self.source.root) )


    def actions(self) -> None:
        '''
        Defines the actions of the ExecutionPanel class.
        '''
        # when the server checkbox is toggled, emit a PyQt6 signal (to start server)
        self.server_checkbox.toggled.connect(self.update_online_state)
        
        # when the lock_button is pressed, enable / disable the widgets
        self.lock_button.toggled.connect(self.set_locked)

        # when the model button is pressed, select the reading folder
        self.model_browse_button.clicked.connect(
            lambda: self.browse_folder(is_model=True)
        )
        
        # when the save button is pressed, select the saving folder
        self.save_browse_button.clicked.connect(
            lambda: self.browse_folder(is_model=False)
        )

        # when the model path is modified, change the default model path
        self.model_path_entry.textChanged.connect(
            self.on_model_path_changed
        )

        # when the saving path is modified, change the default saving path
        self.saving_entry.textChanged.connect(
            self.on_save_path_changed
        )


    def on_model_path_changed(self, path: str) -> None:
        '''Change the default model path in 'app_config.ini' '''
        set_in_config(
            module="interface",
            item="model_path",
            val=path,
        )
        log.debug(f"Model folder modified, new model folder: {path}")


    def on_save_path_changed(self, path: str) -> None:
        '''Change the default saving path in 'app_config.ini' '''
        set_in_config(
            module="interface",
            item="saving_path",
            val=path
        )
        log.debug(f"Saving folder modified, new saving folder: {path}")


    def update_online_state(self, checked: bool) -> None:
        '''Change the server state and emit the realted signal.'''
        if not self.lock_button.isChecked():       # if the lock button is not pressed
            self.server_entry.setEnabled(checked)  # enable / disable the server address label
        
        log.debug("Server box checked." if checked else "Server box unchecked.")
        self.server_state_changed.emit(checked)  # emit a signal to start / stop the server


    def set_locked(self, locked: bool) -> None:
        '''
        Enable / disable every widget of the panel 
        when the lock button is clicked.
        '''
        # list of widgets to lock
        widgets = [
            self.server_checkbox,
            self.model_path_entry,
            self.model_browse_button,
            self.saving_entry,
            self.save_browse_button
        ]

        for w in widgets: # for every widget
            w.setEnabled(not locked) # lock / unlock it (locked = True means disable -> Enable = False)

        # change the button text 
        self.lock_button.setText(
            "🔓 Unlock configuration" if locked else "🔒 Lock configuration"
        )
        log.debug("Configuration locked." if locked else "Configuration unlocked.")

        if not locked:  # if unlocking
            if self.get_path_model() != self.model_path:        # if the current model path != the one registered during locked
                self.model_path_entry.setText(self.model_path)  # set the model path
            
            if self.get_path_saving() != self.save_path:   # if the current saving path != the one registered during locked
                self.saving_entry.setText(self.save_path)  # set the saving path 


    def browse_folder(self, is_model: bool=True) -> None:
        '''
        Open a QFileDialog to select a folder. Modify the model
        or saving entry according to the button used.
        '''
        path = QFileDialog.getExistingDirectory(
            self,
            "Select folder",
            "",             # initial directory ("" = current working dir)
            QFileDialog.Option.ShowDirsOnly
        )

        # if a folder was selected
        if path:
            # update the corresponding entry
            if is_model:
                self.set_path_model(path)
            else:
                self.set_path_saving(path)


    ### helpers

    def get_execution(self) -> dict[str, bool | str]:
        '''
        Return the execution dictionary defining the
        online / offline, reading and saving procedure. 
        '''
        execution = {}
        execution["is_online"] = self.is_online_enabled()
        execution["model_path"] = self.get_path_model()
        execution["saving_path"] = self.get_path_saving()
        execution["server_address"] = self.get_server_address()

        return execution

        # checkers
    def is_online_enabled(self) -> bool:
        return self.server_checkbox.isChecked()

    def is_locked(self) -> bool:
        return self.lock_button.isChecked()

        # getters
    def get_path_model(self) -> str:
        return self.model_path_entry.text().strip()

    def get_path_saving(self) -> str:
        return self.saving_entry.text().strip()
    
    def get_server_address(self) -> str:
        return self.server_entry.text().strip()

        
        ### setters
    def set_path_model(self, path: str) -> None:
        if not self.is_locked():
            log.info(f"Model path setted: '{path}'")
            self.model_path_entry.setText(path)
        else:
            log.info(f"Configuration locked, model path unchanged before unlocking.")
        self.model_path = path
    
    def set_path_saving(self, path: str) -> None:
        if not self.is_locked():
            log.info(f"Saving path setted: '{path}'")
            self.saving_entry.setText(path)
        else:
            log.info(f"Configuration locked, saving path unchanged before unlocking.")
        self.save_path = path
    
    def set_server_address(self, address: str) -> None:
        return self.server_entry.setText(address)
