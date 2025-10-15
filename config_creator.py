"""
PyQt6 Config File Creator

Run: python config_creator.py

"""

import json
import sys
from pathlib import Path
from utils.getter import get_classes
from config.input_qt_config import InputRow, ObjectiveRow

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
        self.input_classes = get_classes("inputs")
        self.input_group = QGroupBox("Available Inputs")
        self.input_layout = QVBoxLayout()

        self.input_rows: dict[str, InputRow] = {}

        for name, cls in self.input_classes.items():
            row = InputRow(name, cls)
            self.input_layout.addWidget(row)
            self.input_rows[name] = row

        self.input_group.setLayout(self.input_layout)
        main_layout.addWidget(self.input_group)

        # --- Block 3: Objectives ---
        self.objective_classes = get_classes("objectives")
        self.objective_group = QGroupBox("Available Objectives")
        self.objective_layout = QVBoxLayout()

        # for name, cls in self.objective_classes.items():
        #     cb = QCheckBox(name)
        #     self.objective_layout.addWidget(cb)
        #     cb.setToolTip("Add this objective to the model.")

        self.objective_rows: dict[str, ObjectiveRow] = {}
        for name, cls in self.objective_classes.items():    # or objective_classes.keys()
            row = ObjectiveRow(name)
            self.objective_layout.addWidget(row)  # whatever layout/groupbox you created
            self.objective_rows[name] = row
        
        self.objective_group.setLayout(self.objective_layout)
        main_layout.addWidget(self.objective_group)


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
        """
        Build structured config ready to be dumped as JSON.
        Assumes self.input_rows: dict[name, InputRow]
        """
        input_list = []
        for name, row in self.input_rows.items():
            sel = bool(row.is_enabled())
            val = row.get_value()            # -> (lo, hi) or None
            safe = getattr(row, "safe_bounds", None)
            input_list.append({
                "name": name,
                "selected": sel,
                "bounds": list(val) if val is not None else None,
                "safe_bounds": list(safe) if safe is not None else None,
            })

        objective_list = []
        for name, row in self.objective_rows.items():
            obj = row.get_dict()
            objective_list.append(obj)

        other = {
            "created_by": "user",
            "notes": ""
        }

        cfg = {
            "inputs": input_list,
            "objectives": objective_list,
            "other": other,
        }

        # convenience boolean if you need it elsewhere
        self.has_any_input_selected = any(item["selected"] for item in input_list)
        self.has_any_objective_selected = any(item["selected"] for item in objective_list)

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
        if not self.has_any_input_selected:
            return False, "Please enable at least one input option."
        return True, ""

    def on_validate(self):
        ok, msg = self.validate_inputs()
        if not ok:
            QMessageBox.warning(self, "Validation failed", msg)
            return
        
        cfg = self.collect_config()
        
        if not self.has_any_input_selected:
            QMessageBox.warning(self, "Validation failed", "Please enable at least one input option.")
            return
        elif not self.has_any_objective_selected:
            QMessageBox.warning(self, "Validation failed", "Please enable at least one objective option.")
            return

        # Ensure every selected input has valid bounds
        missing_bounds = []
        for name, row in self.input_rows.items():
            if row.is_enabled() and row.get_value() is None:
                missing_bounds.append(name)
        if missing_bounds:
            QMessageBox.warning(
                self,
                "Validation failed",
                "The following selected inputs have missing or invalid bounds:\n" + ", ".join(missing_bounds)
            )
            return

        target = Path(self.path_edit.text().strip())

        # Overwrite prompt if file exists
        if target.exists():
            reply = QMessageBox.question(
                self,
                "Overwrite file?",
                f"The file {target!s} already exists. Do you want to overwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        tmp = target.with_suffix(target.suffix + ".tmp") # create a temporary (tmp) version
        try:
            with tmp.open("w", encoding="utf-8") as f: # writing on tmp version to avoid Python buffer lost in case of exception, leading to truncating issues
                json.dump(cfg, f, indent=4, ensure_ascii=False)
                f.flush()  # forces the data out of the Python buffer to the OS, avoid empty json
            tmp.replace(target)  # swap files
        except Exception as e:
            QMessageBox.critical(self, "Write error", f"Failed to write file: {e}")
            return

        QMessageBox.information(self, "Success", f"Configuration saved to {target!s}")


if __name__ == "__main__":

    app = QApplication(sys.argv)
    w = ConfigCreatorWindow()
    w.show()
    sys.exit(app.exec())
