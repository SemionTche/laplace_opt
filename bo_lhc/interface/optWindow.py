from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QGridLayout,
    QVBoxLayout, QHBoxLayout, QMessageBox, QLineEdit, QPushButton, QGroupBox, QFileDialog, QCheckBox
)
from PyQt6.QtCore import Qt, QSettings, QTimer
from PyQt6.QtGui import QIcon

from utils.getter import get_classes
from config.qt_config import InputRow, ObjectiveRow

import qdarkstyle
import pathlib
import json

# project
from interface.executionPanel import ExecutionPanel

class OptWindow(QMainWindow):
    
    def __init__(self):

        super().__init__() # heritage from QMainWindow

        # Set window title
        self.setWindowTitle("Optimization Window")
        p = pathlib.Path(__file__)
        icon_path = p.parent / 'icons'

        # self.settings = QSettings(str(p.parent / "interface.ini"), QSettings.Format.IniFormat)

        self.setWindowIcon(QIcon(str(icon_path / 'LOA.png')))
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        self.setGeometry(100, 30, 1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        # main_layout.setContentsMargins(12, 12, 12, 12)
        # main_layout.setSpacing(10)


        # --- Block 1: Path chooser / Toggles ---
        self.execution_panel = ExecutionPanel()
        main_layout.addWidget(self.execution_panel)

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

        self.objective_rows: dict[str, ObjectiveRow] = {}
        for name, cls in self.objective_classes.items():
            row = ObjectiveRow(name)
            self.objective_layout.addWidget(row)
            self.objective_rows[name] = row
        
        self.objective_group.setLayout(self.objective_layout)
        main_layout.addWidget(self.objective_group)


        # --- Bottom: Validate and Create Button ---
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        self.validate_btn = QPushButton("Validate and Create")
        self.validate_btn.clicked.connect(self.on_validate)
        bottom_layout.addWidget(self.validate_btn)

        main_layout.addLayout(bottom_layout)


    def on_lock_toggled(self, locked: bool):
        widgets = [
            self.chk_online,
            self.chk_file,
            self.chk_server,
            self.path_edit,
            self.browse_btn,
        ]

        for w in widgets:
            w.setEnabled(not locked)

        # server address depends on online checkbox + lock state
        self.server_addr_edit.setEnabled(self.chk_online.isChecked() and not locked)

        self.lock_btn.setText("🔓 Unlock configuration" if locked else "🔒 Lock configuration")





    def toggle_enable_state(self):
        state = not self.toggle_left.isEnabled()
        self.toggle_left.setEnabled(state)
        self.toggle_right.setEnabled(state)


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
            val = row.get_value()            # -> (lo, hi) or None
            safe = getattr(row, "safe_bounds", None)
            input_list.append({
                "name": name,
                "selected": bool(row.is_enabled()),
                "bounds": list(val) if val is not None else None,
                "safe_bounds": list(safe) if safe is not None else None,
            })

        objective_list = []
        for name, row in self.objective_rows.items():
            objective_list.append({
                "name": row.name,
                "selected": row.is_selected(),
                "minimize": row.is_minimize(),
            })

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


    def validate_form(self):
        target = self.path_edit.text().strip()
        
        if not target:
            return False, "Please choose a destination file path."
        
        # Ensure parent dir is writable
        target_path = pathlib.Path(target)
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
        elif not self.has_any_objective_selected:
            return False, "Please enable at least one objective option."
        
        # Ensure every selected input has valid bounds
        missing_bounds = []
        for name, row in self.input_rows.items():
            if row.is_enabled() and row.get_value() is None:
                missing_bounds.append(name)
        if missing_bounds:
            return False, "The following selected inputs have missing or invalid bounds:\n" + ", ".join(missing_bounds)
        
        return True, ""

    def on_validate(self):
        ok, msg = self.validate_form()
        if not ok:
            QMessageBox.warning(self, "Validation failed", msg)
            return
        
        cfg = self.collect_config()

        target = pathlib.Path(self.path_edit.text().strip())

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