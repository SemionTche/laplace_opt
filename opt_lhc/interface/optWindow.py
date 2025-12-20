# libraries
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QMessageBox, QPushButton, QGroupBox
)
from PyQt6.QtGui import QIcon

import qdarkstyle
import pathlib
import json

# project
from interface.executionPanel import ExecutionPanel
from interface.rowPanel import RowPanel
from interface.inputRow import InputRow
from interface.objectiveRow import ObjectiveRow

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
        self.validate_btn.clicked.connect(self.on_validate)
        bottom_layout.addWidget(self.validate_btn)

        main_layout.addLayout(bottom_layout)


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