# utils/standard_widgets.py

from PyQt6.QtWidgets import (
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
)
from PyQt6.QtCore import Qt

from utils.pathSelectorWidget import PathSelectorWidget


# ---------------------------------------------------------------------
# 1. PLACE (LABEL, WIDGET) PAIRS IN A GRID
# ---------------------------------------------------------------------

def place_labeled_widgets(
    layout,
    items: list[tuple[str, object]],
    *,
    max_per_row: int = 6,
):
    """
    Place (label, widget) pairs in a QGridLayout.

    Layout pattern:
        label  label  label
        widget widget widget
    """
    col = 0
    base_row = 0

    for label_text, widget in items:
        if col >= max_per_row:
            col = 0
            base_row += 2

        label = QLabel(label_text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label, base_row, col)
        layout.addWidget(widget, base_row + 1, col)

        col += 1


# ---------------------------------------------------------------------
# 2. STANDARD PARAMETER WIDGET FACTORY
# ---------------------------------------------------------------------

def create_standard_widget(name: str, meta: dict):
    """
    Create a widget from a parameter metadata dict.
    """
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


# ---------------------------------------------------------------------
# 3. LOAD STANDARD PARAMETER WIDGETS (USES THE PLACER)
# ---------------------------------------------------------------------

def load_standard_widgets(
    layout,
    parameters: dict,
    *,
    max_per_row: int = 6,
):
    """
    Create and place parameter widgets using a standard layout.

    Returns:
        dict[str, QWidget]
    """
    items = []
    widgets = {}

    for name, meta in parameters.items():
        w = create_standard_widget(name, meta)
        label = meta.get("label", name)

        items.append((label, w))
        widgets[name] = w

    place_labeled_widgets(
        layout,
        items,
        max_per_row=max_per_row,
    )

    return widgets
