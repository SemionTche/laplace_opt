# libraries
from PyQt6.QtWidgets import (
    QGroupBox, QGridLayout, QRadioButton,
    QCheckBox, QLineEdit, QPushButton, QLabel, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal


class ExecutionPanel(QGroupBox):
    '''
    Panel handling execution mode and data source configuration.
    A lock button allows to enable / disable every widget.
    '''
    # signal indicating that that the server state changed
    # connected to "launch_server" in OptWindow
    server_state_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__("Execution & Data Configuration")

        self.set_up() # build the elements
        self.actions() # defines the panel actions


    def set_up(self) -> None:
        '''
        Function made to create and set the elements
        of the ExecutionPanel class.
        '''
        exc_layout = QGridLayout(self)

        # Online execution
        self.server_checkbox = QCheckBox("Run online (start server)")
        self.server_label = QLabel("")
        self.server_label.setEnabled(False)

        # Data source
            # file
        self.read_file = QRadioButton("Read data from file")
        self.read_file.setChecked(True)
        self.read_entry = QLineEdit()
        self.read_entry.setPlaceholderText("reading path")
        self.read_browse_button = QPushButton("Read Browse")

            # server
        self.read_server = QRadioButton("Read data from server")
        self.read_server.setEnabled(False)

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
        exc_layout.addWidget(self.server_label, 0, 2)

        exc_layout.addWidget(self.read_file, 1, 0)
        exc_layout.addWidget(QLabel("Reading path:"), 1, 1)
        exc_layout.addWidget(self.read_entry, 1, 2)
        exc_layout.addWidget(self.read_browse_button, 1, 3)

        exc_layout.addWidget(self.read_server, 2, 0)

        exc_layout.addWidget(QLabel("Saving path:"), 2, 1)
        exc_layout.addWidget(self.saving_entry, 2, 2)
        exc_layout.addWidget(self.save_browse_button, 2, 3)

        exc_layout.addWidget(self.lock_button, 0, 3, alignment=Qt.AlignmentFlag.AlignRight)

        exc_layout.setColumnStretch(2, 1)

        self.update_read_server_state() # enable / disable the read_server radiobutton
        self.update_read_file_state()   # enable / disable the read_entry


    def actions(self) -> None:
        '''
        Defines the action of the ExecutionPanel class.
        '''
        # server connection
        self.server_checkbox.toggled.connect(self.update_online_state)
        
        # read from file
        self.read_file.toggled.connect(self.update_read_file_state)
        
        # lock the widgets
        self.lock_button.toggled.connect(self.set_locked)

        # select the reading folder
        self.read_browse_button.clicked.connect(
            lambda: self.browse_folder(is_read=True)
        )
        
        # select the saving folder
        self.save_browse_button.clicked.connect(
            lambda: self.browse_folder(is_read=False)
        )


    def update_online_state(self, checked: bool) -> None:
        '''
        Change the server state and emit signal realted.
        '''
        if not self.lock_button.isChecked():
            self.server_label.setEnabled(checked) # enable / disable the server address label
        
        self.update_read_server_state()  # enable / disable the read_server radiobutton
        
        self.server_state_changed.emit(checked) # emit a signal to start / stop the server


    def update_read_server_state(self) -> None:
        '''
        Enable read_server only if:
            - server is enabled
            - configuration is not locked
        '''
        enabled = (
            self.server_checkbox.isChecked()
            and not self.lock_button.isChecked()
        )
        self.read_server.setEnabled(enabled)
    

    def update_read_file_state(self) -> None:
        '''
        Enable file reading widgets only if:
            - read_file is selected
            - configuration is not locked
        '''
        enabled = (
            self.read_file.isChecked()
            and not self.lock_button.isChecked()
        )
        self.read_entry.setEnabled(enabled)
        self.read_browse_button.setEnabled(enabled)


    def set_locked(self, locked: bool) -> None:
        '''
        Enable / disable every widget of the panel when
        the lock button is clicked.
        '''
        widgets = [   # list of all widgets of the panel
            self.server_checkbox,
            self.read_file,
            self.read_entry,
            self.read_browse_button,
            self.saving_entry,
            self.save_browse_button
        ]

        for w in widgets: # for every widget
            w.setEnabled(not locked) # lock / unlock it (locked = True means disable: Enable = False)

        # for the server label (address), we need to verify if it is in server mode 
        # otherwise the widget might not exist (if server did not run at all)
        # and is anyway already disable if the server is off
        self.server_label.setEnabled(
            self.server_checkbox.isChecked() and not locked
        )

        self.update_read_server_state()
        self.update_read_file_state()

        # change the text of the button
        self.lock_button.setText(
            "🔓 Unlock configuration" if locked else "🔒 Lock configuration"
        )


    def browse_folder(self, is_read: bool=True) -> None:
        '''
        Open a QFileDialog to select a folder. Modify the reading
        or saving entry according to the button used.
        '''
        path = QFileDialog.getExistingDirectory(self,
                                                "Select folder",
                                                "",  # initial directory ("" = current working dir)
                                                QFileDialog.Option.ShowDirsOnly)

        if path: # if a folder was selected
            # update the corresponding entry
            if is_read:
                self.read_entry.setText(path)
            else:
                self.saving_entry.setText(path)

    ### helpers

    def get_execution(self) -> dict[str, bool]:
        '''
        Return the execution dictionary defining the
        online / offline, reading and saving procedures. 
        '''
        execution = {}
        execution["in_online"] = self.is_online_enabled()
        execution["is_reading_file"] = self.read_from_file()
        execution["reading_path"] = self.get_path_reading()
        execution["saving_path"] = self.get_path_saving()
        execution["server_address"] = self.get_server_address()

        return execution


    def is_online_enabled(self) -> bool:
        return self.server_checkbox.isChecked()

    def is_locked(self) -> bool:
        return self.lock_button.isChecked()

    def read_from_file(self) -> bool:
        return self.read_file.isChecked()

    def read_from_server(self) -> bool:
        return self.read_server.isChecked()

    def get_path_reading(self) -> str:
        return self.read_entry.text().strip()

    def get_path_saving(self) -> str:
        return self.saving_entry.text().strip()
    
    def get_server_address(self) -> str:
        return self.server_label.text().strip()

    def set_path_reading(self, path: str) -> None:
        self.read_entry.setText(path)
    
    def set_path_saving(self, path: str) -> None:
        self.saving_entry.setText(path)
    
    def set_server_address(self, address: str) -> None:
        return self.server_label.setText(address)
