# libraries
from PyQt6.QtWidgets import (
    QGroupBox, QGridLayout, QRadioButton,
    QCheckBox, QLineEdit, QPushButton, QLabel, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal

from laplace_log import log

# project
from ...utils.config_helper import get_from_config, set_in_config


class ExecutionPanel(QGroupBox):
    '''
    Panel handling execution mode and data source configuration.
    A lock button allows to enable / disable every widget.
    '''
    # signal indicating that the server checkbox state changed
    server_state_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__("Execution & Data Configuration")

        self.set_up()  # build the elements
        self.actions() # defines the panel actions


    def set_up(self) -> None:
        '''
        Function made to create and set the elements
        of the ExecutionPanel class.
        '''
        exc_layout = QGridLayout(self)

        # Online execution
        self.server_checkbox = QCheckBox("Run online (start server)")
        self.server_entry = QLineEdit("")  # indicates the optimization server address
        self.server_entry.setReadOnly(True)

        # Data source
            # file
        self.read_file = QRadioButton("Read data from file")
        self.read_file.setChecked(True)  # default mode read from file
        self.read_entry = QLineEdit()
        self.read_entry.setPlaceholderText("reading path")
        self.read_browse_button = QPushButton("Read Browse")

            # server
        self.read_server = QRadioButton("Read data from server")
        self.read_server.setEnabled(False) # cannot read from server until server connected

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

        exc_layout.addWidget(self.read_file, 1, 0)
        exc_layout.addWidget(QLabel("Reading path:"), 1, 1)
        exc_layout.addWidget(self.read_entry, 1, 2)
        exc_layout.addWidget(self.read_browse_button, 1, 3)

        exc_layout.addWidget(self.read_server, 2, 0)

        exc_layout.addWidget(QLabel("Saving path:"), 2, 1)
        exc_layout.addWidget(self.saving_entry, 2, 2)
        exc_layout.addWidget(self.save_browse_button, 2, 3)

        exc_layout.addWidget(self.lock_button, 0, 3, alignment=Qt.AlignmentFlag.AlignRight)

        exc_layout.setColumnStretch(2, 1) # set the Stretch of the 2nd column, to 1 (other are 0)

        self.update_read_server_state() # enable / disable the read_server radiobutton
        self.update_read_file_state()   # enable / disable the read_entry

        # get the default execution (reading and saving) path
            # get and set default saving path
        default_saving_path = get_from_config(
            module="interface",
            item="default_saving_path",
            default_value="",
            type=str
        )
        self.set_path_saving(default_saving_path)
        
            # get and set default reading path
        default_reading_path = get_from_config(
            module="interface",
            item="default_reading_path",
            default_value="",
            type=str
        )
        self.set_path_reading(default_reading_path)


    def actions(self) -> None:
        '''
        Defines the actions of the ExecutionPanel class.
        '''
        # when the server checkbox is toggled, emit a PyQt6 signal (to start server)
        self.server_checkbox.toggled.connect(self.update_online_state)
        
        # when the read from file radiobutton is toggled, enable / disable the read_entry
        self.read_file.toggled.connect(self.update_read_file_state)
        
        # when the lock_button is pressed, enable / disable the widgets
        self.lock_button.toggled.connect(self.set_locked)

        # when the read button is pressed, select the reading folder
        self.read_browse_button.clicked.connect(
            lambda: self.browse_folder(is_read=True)
        )
        
        # when the save button is pressed, select the saving folder
        self.save_browse_button.clicked.connect(
            lambda: self.browse_folder(is_read=False)
        )

        # when the reading path is modified, change the default reading path
        self.read_entry.textChanged.connect(
            self.on_read_path_changed
        )

        # when the saving path is modified, change the default saving path
        self.saving_entry.textChanged.connect(
            self.on_save_path_changed
        )


    def on_read_path_changed(self, path: str) -> None:
        '''
        Change the default reading path in 'config.ini' and
        display it in the logs.
        '''
        set_in_config(
            module="interface",
            item="default_reading_path",
            val=path
        )
        log.debug(f"Reading folder modified, new reading folder: {path}")


    def on_save_path_changed(self, path: str) -> None:
        '''
        Change the default saving path in 'config.ini' and
        display it in the logs.
        '''
        set_in_config(
            module="interface",
            item="default_saving_path",
            val=path
        )
        log.debug(f"Saving folder modified, new saving folder: {path}")


    def update_online_state(self, checked: bool) -> None:
        '''
        Change the server state and emit the realted signal.
        '''
        if not self.lock_button.isChecked():       # if the lock button is not pressed
            self.server_entry.setEnabled(checked)  # enable / disable the server address label
        
        self.update_read_server_state()  # enable / disable the read_server radiobutton
        
        self.read_server.setChecked(checked)     # check the server reading radio button
        self.read_file.setChecked(not checked)   # uncheck the file reading radio button
        
        log.debug("Server box checked." if checked else "Server box unchecked.")
        self.server_state_changed.emit(checked)  # emit a signal to start / stop the server


    def update_read_server_state(self) -> None:
        '''
        Enable / disable the server reading radiobutton.

        Enable read_server if server checkbox is enabled
        and configuration is not locked.
        '''
        enabled = (
            self.server_checkbox.isChecked()      # if the server box is checked 
            and not self.lock_button.isChecked()  # and the lock button not pressed
        )
        self.read_server.setEnabled(enabled)   # enable / disable the server reading radiobutton
        self.saving_entry.setReadOnly(enabled) # in server mode, cannot change the saving path


    def update_read_file_state(self) -> None:
        '''
        Enable / disable the file reading widgets.

        Enable read file widgets (entry and button) 
        if read_file radiobutton is selected and
        configuration not locked.
        '''
        enabled = (
            self.read_file.isChecked()            # if the read file radiobutton is checked
            and not self.lock_button.isChecked()  # and the lock button not pressed
        )

        # enable / disable the reading entry and button
        self.read_entry.setEnabled(enabled)
        self.read_browse_button.setEnabled(enabled)


    def set_locked(self, locked: bool) -> None:
        '''
        Enable / disable every widget of the panel when
        the lock button is clicked.
        '''
        # list of widgets to lock
        widgets = [
            self.server_checkbox,
            self.read_file,
            self.read_entry,
            self.read_browse_button,
            self.read_server,
            self.saving_entry,
            self.save_browse_button
        ]

        for w in widgets: # for every widget
            w.setEnabled(not locked) # lock / unlock it (locked = True means disable -> Enable = False)

        # lock / unlock the server radiobutton and the 
        # reading widgets according to the current chosen mode
        self.update_read_server_state()
        self.update_read_file_state()

        # change the button text 
        self.lock_button.setText(
            "🔓 Unlock configuration" if locked else "🔒 Lock configuration"
        )
        log.debug("Configuration locked." if locked else "Configuration unlocked.")


    def browse_folder(self, is_read: bool=True) -> None:
        '''
        Open a QFileDialog to select a folder. Modify the reading
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
            if is_read:
                self.set_path_reading(path)
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
        execution["is_reading_file"] = self.read_from_file()
        execution["reading_path"] = self.get_path_reading()
        execution["saving_path"] = self.get_path_saving()
        execution["server_address"] = self.get_server_address()

        return execution


        # checkers
    def is_online_enabled(self) -> bool:
        return self.server_checkbox.isChecked()

    def is_locked(self) -> bool:
        return self.lock_button.isChecked()

    def read_from_file(self) -> bool:
        return self.read_file.isChecked()

    def read_from_server(self) -> bool:
        return self.read_server.isChecked()


        # getters
    def get_path_reading(self) -> str:
        return self.read_entry.text().strip()

    def get_path_saving(self) -> str:
        return self.saving_entry.text().strip()
    
    def get_server_address(self) -> str:
        return self.server_entry.text().strip()

        
        ### setters
    def set_path_reading(self, path: str) -> None:
        if not self.is_locked():
            log.info(f"Reading path setted: '{path}'")
            self.read_entry.setText(path)
    
    def set_path_saving(self, path: str) -> None:
        if not self.is_locked():
            log.info(f"Saving path setted: '{path}'")
            self.saving_entry.setText(path)
    
    def set_server_address(self, address: str) -> None:
        return self.server_entry.setText(address)
