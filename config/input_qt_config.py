from typing import Optional, Tuple

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QCheckBox, QLabel, QLineEdit, QComboBox
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import Qt, QRegularExpression

class InputRow(QWidget):
    def __init__(self, name: str, cls: type):
        super().__init__()
        self.name = name
        self.cls = cls

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setToolTip(f"Enable {name}")
        layout.addWidget(self.checkbox)

        # label for the input name (display)
        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.name_label.setFixedWidth(200)  # tweak to taste
        layout.addWidget(self.name_label)

        # bounds edit
        self.bounds_edit = QLineEdit()
        self.bounds_edit.setPlaceholderText("min,max")
        self.bounds_edit.setEnabled(False)  # disabled until checkbox checked
        # regex to accept floats optionally with spaces around comma
        rx = QRegularExpression(r'^\s*-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?\s*$')
        self.bounds_edit.setValidator(QRegularExpressionValidator(rx, self))
        layout.addWidget(self.bounds_edit, stretch=1)

        # safe bounds label
        self.safe_label = QLabel("safe: n/a")
        self.safe_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        self.safe_label.setFixedWidth(120)
        layout.addWidget(self.safe_label)

        # attempt to obtain safe_bounds from class (lightweight): prefer cls.default()
        try:
            if hasattr(cls, "default") and callable(getattr(cls, "default")):
                inst = cls.default()
            else:
                inst = cls()
            sb = getattr(inst, "safe_bounds", None)
        except Exception:
            sb = None

        self.safe_bounds = tuple(sb) if sb is not None else None
        if self.safe_bounds:
            self.safe_label.setText(f"safe: {self.safe_bounds}")

        # signals
        self.checkbox.stateChanged.connect(self._on_checkbox_changed)  # note: state is int
        self.bounds_edit.textChanged.connect(self._on_bounds_changed)

    def _on_checkbox_changed(self, state: int) -> None:
        enabled = bool(state)
        self.bounds_edit.setEnabled(enabled)
        # optionally change style of label to indicate enabled/disabled
        self.name_label.setEnabled(enabled)
        if not enabled:
            # reset styles
            self.bounds_edit.setStyleSheet("")
            self.safe_label.setStyleSheet("")

    def _on_bounds_changed(self, text: str) -> None:
        # quick visual feedback using validator + safe_bounds checks
        if not text:
            self.bounds_edit.setStyleSheet("")
            self.safe_label.setStyleSheet("")
            return

        # validator already ensures format; attempt parse
        try:
            lo_str, hi_str = (p.strip() for p in text.split(",", 1))
            lo, hi = float(lo_str), float(hi_str)
        except Exception:
            self.bounds_edit.setStyleSheet("border: 1px solid red;")
            return

        if self.safe_bounds is None:
            self.bounds_edit.setStyleSheet("")
            return

        safe_lo, safe_hi = self.safe_bounds
        if lo < safe_lo or hi > safe_hi or lo >= hi:
            self.bounds_edit.setStyleSheet("border: 1px solid red;")
            self.safe_label.setStyleSheet("color: red;")
        else:
            self.bounds_edit.setStyleSheet("")
            self.safe_label.setStyleSheet("color: black;")

    def get_value(self) -> Optional[Tuple[float, float]]:
        """Return (lo, hi) if parseable and valid and checkbox is checked, else None."""
        if not self.checkbox.isChecked():
            return None
        txt = self.bounds_edit.text().strip()
        if not txt:
            return None
        try:
            lo_str, hi_str = (p.strip() for p in txt.split(",", 1))
            lo, hi = float(lo_str), float(hi_str)
        except Exception:
            return None
        if self.safe_bounds:
            safe_lo, safe_hi = self.safe_bounds
            if lo < safe_lo or hi > safe_hi or lo >= hi:
                return None
        return (lo, hi)

    def is_enabled(self) -> bool:
        return self.checkbox.isChecked()


class ObjectiveRow(QWidget):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # selected checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setToolTip(f"Include objective '{name}' in config")
        layout.addWidget(self.checkbox)

        # name label
        self.label = QLabel(name)
        layout.addWidget(self.label)

        # minimize/maximize selector
        self.mode = QComboBox()
        self.mode.addItems(["Minimize", "Maximize"])
        self.mode.setToolTip("Choose whether to minimize or maximize this objective")
        layout.addWidget(self.mode)

    def is_selected(self) -> bool:
        return self.checkbox.isChecked()

    def is_minimize(self) -> bool:
        return self.mode.currentText() == "Minimize"

    def get_dict(self) -> dict:
        """Return JSON-serializable dict for this objective."""
        return {
            "name": self.name,
            "selected": self.is_selected(),
            "minimize": self.is_minimize(),
        }