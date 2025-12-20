from typing import Optional, Tuple
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QCheckBox, QLabel, QDoubleSpinBox
)
from PyQt6.QtCore import Qt


class InputRow(QWidget):
    def __init__(self, name: str, cls: type):
        super().__init__()
        self.name = name
        self.cls = cls

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # --- Checkbox ---
        self.checkbox = QCheckBox()
        self.checkbox.setToolTip(f"Enable {name}")
        layout.addWidget(self.checkbox)

        # --- Label ---
        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.name_label.setFixedWidth(200)
        layout.addWidget(self.name_label)

        # --- Min / Max SpinBoxes ---
        self.min_spin = QDoubleSpinBox()
        self.max_spin = QDoubleSpinBox()
        self.min_spin.setDecimals(6)
        self.max_spin.setDecimals(6)
        self.min_spin.setEnabled(False)
        self.max_spin.setEnabled(False)
        layout.addWidget(self.min_spin)
        layout.addWidget(self.max_spin)

        # --- Safe bounds ---
        self.safe_label = QLabel("safe: n/a")
        self.safe_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        self.safe_label.setFixedWidth(120)
        layout.addWidget(self.safe_label)

        # --- Obtain safe bounds from class ---
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
            safe_lo, safe_hi = self.safe_bounds
            self.min_spin.setMinimum(safe_lo)
            self.min_spin.setMaximum(safe_hi)
            self.max_spin.setMinimum(safe_lo)
            self.max_spin.setMaximum(safe_hi)
            self.min_spin.setValue(safe_lo)
            self.max_spin.setValue(safe_hi)
            self.safe_label.setText(f"safe: {self.safe_bounds}")

        # --- Signals ---
        self.checkbox.stateChanged.connect(self._on_checkbox_changed)
        self.min_spin.valueChanged.connect(self._on_spin_changed)
        self.max_spin.valueChanged.connect(self._on_spin_changed)

    # --- Enable / disable ---
    def _on_checkbox_changed(self, state: int) -> None:
        enabled = bool(state)
        self.min_spin.setEnabled(enabled)
        self.max_spin.setEnabled(enabled)
        self.name_label.setEnabled(enabled)
        if not enabled:
            self.min_spin.setStyleSheet("")
            self.max_spin.setStyleSheet("")
            self.safe_label.setStyleSheet("")

    # --- Validation / warning ---
    def _on_spin_changed(self, value):
        if not self.checkbox.isChecked():
            return

        lo = self.min_spin.value()
        hi = self.max_spin.value()

        invalid = False

        if self.safe_bounds:
            safe_lo, safe_hi = self.safe_bounds
            if lo < safe_lo or hi > safe_hi or lo >= hi:
                invalid = True

        # Update styles
        if invalid:
            self.min_spin.setStyleSheet("border: 1px solid red;")
            self.max_spin.setStyleSheet("border: 1px solid red;")
            self.safe_label.setStyleSheet("color: red;")
        else:
            self.min_spin.setStyleSheet("")
            self.max_spin.setStyleSheet("")
            self.safe_label.setStyleSheet("color: black;")

    # --- API ---
    def get_value(self) -> Optional[Tuple[float, float]]:
        if not self.checkbox.isChecked():
            return None
        lo = self.min_spin.value()
        hi = self.max_spin.value()
        if self.safe_bounds:
            safe_lo, safe_hi = self.safe_bounds
            if lo < safe_lo or hi > safe_hi or lo >= hi:
                return None
        return (lo, hi)

    def is_enabled(self) -> bool:
        return self.checkbox.isChecked()
