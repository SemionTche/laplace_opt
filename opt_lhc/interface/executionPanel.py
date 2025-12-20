from PyQt6.QtWidgets import (
    QGroupBox, QGridLayout, QRadioButton,
    QCheckBox, QLineEdit, QPushButton, QLabel, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal


class ExecutionPanel(QGroupBox):
    """
    Panel handling execution mode and data source configuration.
    """
    server_state_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__("Execution & Data Configuration")

        self.set_up()
        self.actions()


    def set_up(self):
        layout = QGridLayout(self)

        # Online execution
        self.server_checkbox = QCheckBox("Run online (start server)")
        self.server_label = QLabel("")
        self.server_label.setEnabled(False)

        # Data source
            # file
        self.read_file = QRadioButton("Read data from file")
        self.read_file.setChecked(True)
        self.path_file = QLineEdit()
        self.path_file.setPlaceholderText("reading path")
        self.browse_button = QPushButton("Browse")

            # server
        self.read_server = QRadioButton("Read data from server")

        # Saving entry
        self.saving_entry = QLineEdit()
        self.saving_entry.setPlaceholderText("saving path")

        # Lock
        self.lock_button = QPushButton("🔒 Lock configuration")
        self.lock_button.setCheckable(True)

        # Layout
        layout.addWidget(self.server_checkbox, 0, 0)
        layout.addWidget(QLabel("Server address:"), 0, 1)
        layout.addWidget(self.server_label, 0, 2)

        layout.addWidget(self.read_file, 1, 0)
        layout.addWidget(QLabel("Reading path:"), 1, 1)
        layout.addWidget(self.path_file, 1, 2)
        layout.addWidget(self.browse_button, 1, 3)

        layout.addWidget(self.read_server, 2, 0)

        layout.addWidget(QLabel("Saving path:"), 2, 1)
        layout.addWidget(self.saving_entry, 2, 2)
        layout.addWidget(self.lock_button, 3, 3, alignment=Qt.AlignmentFlag.AlignRight)

        layout.setColumnStretch(2, 1)


    def actions(self):
        self.server_checkbox.toggled.connect(self.update_online_state)
        self.read_file.toggled.connect(self.update_file_state)
        self.lock_button.toggled.connect(self.set_locked)

        self.browse_button.clicked.connect(self.browse_file)

    def update_online_state(self, checked: bool):
        print("this is used")
        if not self.lock_button.isChecked():
            self.server_label.setEnabled(checked)
        print(f"checking {checked}")
        self.server_state_changed.emit(checked)

    def update_file_state(self, checked: bool):
        if not self.lock_button.isChecked():
            self.path_file.setEnabled(checked)
            self.browse_button.setEnabled(checked)

    def set_locked(self, locked: bool):
        widgets = [
            self.server_checkbox,
            self.read_file,
            self.read_server,
            self.path_file,
            self.browse_button,
            self.saving_entry
        ]

        for w in widgets:
            w.setEnabled(not locked)

        self.server_label.setEnabled(
            self.server_checkbox.isChecked() and not locked
        )

        self.lock_button.setText(
            "🔓 Unlock configuration" if locked else "🔒 Lock configuration"
        )

    def browse_file(self):
        # Open file dialog
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select file",
            "",  # initial directory, empty string = current dir
            "All files (*);;JSON files (*.json);;Text files (*.txt)"
        )
        if path:
            self.path_file.setText(path)

    ### helpers

    def is_online_enabled(self) -> bool:
        return self.server_checkbox.isChecked()

    def read_from_file(self) -> bool:
        return self.read_file.isChecked()

    def read_from_server(self) -> bool:
        return self.read_server.isChecked()

    def get_path_reading(self) -> str:
        return self.path_file.text().strip()

    def set_path_reading(self, path: str):
        self.path_file.setText(path)
    
    def set_server_address(self, address: str):
        return self.server_label.setText(address)

    def is_locked(self) -> bool:
        return self.lock_button.isChecked()
