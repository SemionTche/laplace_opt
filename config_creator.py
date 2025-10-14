"""
PyQt6 Config File Creator

Run: python config_creator.py

"""

import json
import sys
import importlib.util, inspect
from pathlib import Path
from inputs.input_structure import InputStructure

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
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QTextEdit,
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
        self.path_edit.textChanged.connect(self.update_preview)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.on_browse)

        path_layout.addWidget(QLabel("File:"))
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_btn)
        self.path_group.setLayout(path_layout)

        main_layout.addWidget(self.path_group)

        # --- Block 2: Options ---
        self.options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()

        # Example checkboxes
        self.cb_logging = QCheckBox("Enable logging")
        self.cb_logging.setToolTip("If enabled, the application will create logs")
        self.cb_logging.stateChanged.connect(self.update_preview)

        self.cb_cache = QCheckBox("Use cache")
        self.cb_cache.setToolTip("If enabled, caching will be used for faster startup")
        self.cb_cache.stateChanged.connect(self.update_preview)

        self.cb_autoupdate = QCheckBox("Auto-update")
        self.cb_autoupdate.setToolTip("If enabled, the app will check for updates automatically")
        self.cb_autoupdate.stateChanged.connect(self.update_preview)

        # Some additional inputs
        row_username = QHBoxLayout()
        row_username.addWidget(QLabel("Username:"))
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("optional: user or service name")
        self.username_edit.textChanged.connect(self.update_preview)
        row_username.addWidget(self.username_edit)

        row_timeout = QHBoxLayout()
        row_timeout.addWidget(QLabel("Timeout (s):"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 3600)
        self.timeout_spin.setValue(30)
        self.timeout_spin.valueChanged.connect(self.update_preview)
        row_timeout.addWidget(self.timeout_spin)

        options_layout.addWidget(self.cb_logging)
        options_layout.addWidget(self.cb_cache)
        options_layout.addWidget(self.cb_autoupdate)
        options_layout.addLayout(row_username)
        options_layout.addLayout(row_timeout)

        self.options_group.setLayout(options_layout)
        main_layout.addWidget(self.options_group)

        # --- Live Preview ---
        preview_group = QGroupBox("Preview (will be written as JSON)")
        preview_layout = QVBoxLayout()
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        preview_group.setLayout(preview_layout)
        main_layout.addWidget(preview_group, stretch=1)

        # --- Bottom: Validate / Create button ---
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        self.validate_btn = QPushButton("Validate and Create")
        self.validate_btn.clicked.connect(self.on_validate)
        bottom_layout.addWidget(self.validate_btn)

        main_layout.addLayout(bottom_layout)

        # Initialize preview
        self.update_preview()

    def on_browse(self):
        # Use getSaveFileName so user chooses filename and final path in one dialog
        suggested_name = "config.json"
        path, _ = QFileDialog.getSaveFileName(self, "Choose destination file", suggested_name, "JSON files (*.json);;All files (*)")
        if path:
            self.path_edit.setText(path)

    def collect_config(self):
        # Collect all inputs into a Python dict
        cfg = {
            "enable_logging": bool(self.cb_logging.isChecked()),
            "use_cache": bool(self.cb_cache.isChecked()),
            "auto_update": bool(self.cb_autoupdate.isChecked()),
            "username": self.username_edit.text().strip() or None,
            "timeout_seconds": int(self.timeout_spin.value()),
        }
        return cfg

    def update_preview(self):
        cfg = self.collect_config()
        # Convert None to null in JSON by normal serialization
        pretty = json.dumps(cfg, indent=4, ensure_ascii=False)
        self.preview_text.setPlainText(pretty)

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
        if not (cfg["enable_logging"] or cfg["use_cache"] or cfg["auto_update"] or cfg["username"]):
            return False, "Please enable at least one option or provide a username."
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

    inputs_dir = Path(__file__).parent / "inputs"
    class_names: list[str] = []

    for py in inputs_dir.glob("*.py"):
        if py.name in ("__init__.py", "input_structure.py"):
            continue

        spec = importlib.util.spec_from_file_location(py.stem, py)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        for name, cls in inspect.getmembers(mod, inspect.isclass):
            # ensure it's defined in this module and is a subclass of BaseInput
            if cls.__module__ == mod.__name__ and issubclass(cls, InputStructure) and cls is not InputStructure:
                class_names.append(name)

    print(class_names)

    app = QApplication(sys.argv)
    w = ConfigCreatorWindow()
    w.show()
    sys.exit(app.exec())
