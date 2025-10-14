"""
PyQt6 Config File Creator

Run: python config_creator.py

"""

import json
import sys
from pathlib import Path
from utils.get_module_names import get_input_class_names

from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QCheckBox,
)


class ConfigCreatorWindow(QMainWindow):
    
    def __init__(self):
        
        QMainWindow.__init__(self)
        self.setWindowTitle("Config File Creator")
        self.setMinimumSize(640, 480)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)


        # --- Block 1: Path chooser ---
        self.path_group = QGroupBox("Destination")
        path_layout = QHBoxLayout()

        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Choose where to create the config file (e.g. /home/user/config.json)")

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.on_browse)

        path_layout.addWidget(QLabel("File:"))
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_btn)
        self.path_group.setLayout(path_layout)

        main_layout.addWidget(self.path_group)


        # --- Block 2: Inputs ---
        input_class_names = get_input_class_names()
        self.input_group = QGroupBox("Available Inputs")
        self.input_layout = QVBoxLayout()

        # checkboxes
        self.input_checkboxes = {}
        for name in input_class_names:
                cb = QCheckBox(name)
                self.input_layout.addWidget(cb)
                cb.setToolTip("Add this input to the model.")
                tmp = cb.stateChanged.connect(self.collect_config)
                self.input_checkboxes[name] = cb

        self.input_group.setLayout(self.input_layout)
        main_layout.addWidget(self.input_group)


        # --- Bottom: Validate / Create button ---
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        self.validate_btn = QPushButton("Validate and Create")
        self.validate_btn.clicked.connect(self.on_validate)
        bottom_layout.addWidget(self.validate_btn)

        main_layout.addLayout(bottom_layout)


    def on_browse(self):
        # Use getSaveFileName so user chooses filename and final path in one dialog
        suggested_name = "config.json"
        path, _ = QFileDialog.getSaveFileName(self, "Choose destination file", suggested_name, "JSON files (*.json);;All files (*)")
        if path:
            self.path_edit.setText(path)

    def collect_config(self):
        # Collect all inputs into a Python dict
        inputs = {name: cb.isChecked() for name, cb in self.input_checkboxes.items()}

        # Check if at least one input is True
        self.is_one_inout = True
        if not any(inputs.values()):
            # handle the case: no input selected
            self.is_one_inout = False
        
        cfg = {"inputs": inputs}

        return cfg

    def validate_inputs(self):
        target = self.path_edit.text().strip()
        if not target:
            return False, "Please choose a destination file path."
        # Ensure parent dir is writable
        target_path = Path(target)
        parent = target_path.parent
        if not parent.exists():
            try:
                parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return False, f"Cannot create directory {parent!s}: {e}"
        # Basic filename check
        if target_path.suffix.lower() not in (".json", ".conf", ".cfg", ""):
            # allow files without extension, but warn if uncommon extension
            pass
        # Example check: at least one of logging/cache/autoupdate should be set or username provided
        cfg = self.collect_config()
        if not self.is_one_inout:
            return False, "Please enable at least one input option."
        return True, ""

    def on_validate(self):
        ok, msg = self.validate_inputs()
        if not ok:
            QMessageBox.warning(self, "Validation failed", msg)
            return

        target = Path(self.path_edit.text().strip())
        cfg = self.collect_config()
        data = json.dumps(cfg, indent=4, ensure_ascii=False)

        if target.exists():
            reply = QMessageBox.question(
                self,
                "Overwrite file?",
                f"The file {target!s} already exists. Do you want to overwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        try:
            with target.open("w", encoding="utf-8") as f:
                f.write(data)
        except Exception as e:
            QMessageBox.critical(self, "Write error", f"Failed to write file: {e}")
            return

        QMessageBox.information(self, "Success", f"Configuration saved to {target!s}")


if __name__ == "__main__":

    app = QApplication(sys.argv)
    w = ConfigCreatorWindow()
    w.show()
    sys.exit(app.exec())
