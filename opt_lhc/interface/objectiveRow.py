from typing import Optional, Tuple

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QCheckBox, QLabel, QLineEdit, QComboBox
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import Qt, QRegularExpression


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

        self.mode.setEnabled(False)  # disabled by default
        self.checkbox.stateChanged.connect(self.mode.setEnabled)

    def is_selected(self) -> bool:
        return self.checkbox.isChecked()

    def is_minimize(self) -> bool:
        return self.mode.currentText() == "Minimize"