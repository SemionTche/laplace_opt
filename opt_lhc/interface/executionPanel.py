from PyQt6.QtWidgets import (
    QGroupBox, QGridLayout, QRadioButton,
    QCheckBox, QLineEdit, QPushButton, QLabel, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal


class ExecutionPanel(QGroupBox):
    """
    Panel handling execution mode and data source configuration.
    A lock button allows to enable / disable every widget.
    """
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


    def actions(self) -> None:
        '''
        Defines the action of the ExecutionPanel class.
        '''
        # server connection
        self.server_checkbox.toggled.connect(self.update_online_state)
        
        # read from file
        self.read_file.toggled.connect(self.update_file_state)
        
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
            self.server_label.setEnabled(checked)
        self.server_state_changed.emit(checked)


    def update_file_state(self, checked: bool) -> None:
        '''
        Change the reading state. Enable / disable the 
        reading element depending on the state
        '''
        if not self.lock_button.isChecked():
            self.read_entry.setEnabled(checked)
            self.read_browse_button.setEnabled(checked)


    def set_locked(self, locked: bool) -> None:
        '''
        Enable / disable every widget of the panel when
        the lock button is clicked.
        '''
        widgets = [   # list of all widgets of the panel
            self.server_checkbox,
            self.read_file,
            self.read_server,
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

    def is_online_enabled(self) -> bool:
        return self.server_checkbox.isChecked()

    def read_from_file(self) -> bool:
        return self.read_file.isChecked()

    def read_from_server(self) -> bool:
        return self.read_server.isChecked()

    def get_path_reading(self) -> str:
        return self.read_entry.text().strip()

    def set_path_reading(self, path: str):
        self.read_entry.setText(path)
    
    def set_server_address(self, address: str):
        return self.server_label.setText(address)

    def is_locked(self) -> bool:
        return self.lock_button.isChecked()
