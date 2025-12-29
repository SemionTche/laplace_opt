# libraries
from PyQt6.QtWidgets import (
    QLabel, QSpinBox, QDoubleSpinBox, QComboBox,
)
from PyQt6.QtCore import Qt

# project
from utils.pathSelectorWidget import PathSelectorWidget


def create_standard_widget(name: str, 
                           meta: dict,):
    '''
    Create a widget from a parameter metadata dict.
    '''
    ptype = meta["type"]

    if ptype is int:
        w = QSpinBox()
        w.setRange(meta.get("min", 1), meta.get("max", 10_000))
        w.setValue(meta.get("default", 1))

    elif ptype is float:
        w = QDoubleSpinBox()
        w.setDecimals(meta.get("decimals", 3))
        w.setSingleStep(meta.get("step", 0.1))
        w.setRange(meta.get("min", -1e9), meta.get("max", 1e9))
        w.setValue(meta.get("default", 0.0))

    elif ptype is bool:
        w = QComboBox()
        w.addItems(["True", "False"])
        default = meta.get("default", False)
        w.setCurrentIndex(0 if default else 1)

    elif ptype is str and name == "path":
        w = PathSelectorWidget(
            str(meta.get("default", "")),
            meta.get("label", "Browse"),
            mode=meta.get("mode", "file"),
        )

    else:
        raise TypeError(f"Unsupported parameter type: {ptype}")

    return w


def load_standard_widgets(layout,
                          parameters: dict,
                          *,
                          max_per_row: int = 6,):
    '''
    Layout helper
    Populate a QGridLayout with standard widgets.

    Layout pattern:
        label label label
        widget widget widget

    Returns:
        dict[str, QWidget]
    '''
    widgets = {}

    col = 0
    base_row = 0

    for name, meta in parameters.items():
        if col >= max_per_row:
            col = 0
            base_row += 2

        # --- label ---
        label = QLabel(meta.get("label", name))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setToolTip(meta.get("description", ""))
        layout.addWidget(label, base_row, col)

        # --- widget ---
        w = create_standard_widget(name, meta)
        layout.addWidget(w, base_row + 1, col)

        widgets[name] = w
        col += 1

    return widgets
