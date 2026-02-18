# libraries
from PyQt6.QtWidgets import (
    QLabel, QSpinBox, QDoubleSpinBox,
    QComboBox, QWidget, QGridLayout
)
from PyQt6.QtCore import Qt

# project
from .path_standard_widget import PathStandardWidget


def place_labeled_widgets(layout: QGridLayout,
                          items: list[tuple[str, QWidget]],
                          *,
                          max_per_row: int = 6,
                          start_row: int = 0,
                          start_col: int = 0,) -> tuple[int, int]:
    '''
    Place (label, widget) pairs in a QGridLayout.

    Layout pattern:
        label  label  label
        widget widget widget
        
        label     ...
        widget    ...
    
        Args:
            layout: (QGridLayout)
                the layout in which place the items.
            
            items: (list of tuple(str, QWidget))
                list of the label and widget pairs to place.
            
            max_per_row: (int)
                the maximum number of element per row.
                (default 6)
    '''
    row = start_row
    col = start_col

    for label_text, widget in items: # for every widget
        if col >= max_per_row:       # if the line is full
            col = 0                  # restart from first column
            row += 2            # skip 2 lines (label and widget were placed)

        # create the label
        label = QLabel(label_text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # place label and widget
        layout.addWidget(label, row, col)
        layout.addWidget(widget, row + 1, col)

        col += 1  # update the column
    
    return row, col


def create_standard_widget(name: str, meta: dict) -> QWidget:
    '''
    Create a widget from a parameter metadata dictionary.
    The dictionary must contained a 'type' field in order to
    define the corresponding widget.

        Args:
            name: (str)
                the parameter name. (used for path widget)
            
            meta: (dict)
                the metadata containing the parameter default options.
        
        Returns:
            w: (QWidget)
                the standard widget build according to the meta 'type' field.
    '''
    ptype = meta.get("type", None)

    if ptype is None:
        raise ValueError(f"'type' field is missing in the meta dict: {meta}.")

    elif ptype is int:
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
        w.addItem("True", True)
        w.addItem("False", False)
        default = meta.get("default", False)
        w.setCurrentIndex(0 if default else 1)
    
    elif ptype is dict:
        w = QComboBox()
        combo_dict = meta.get("combo", {})

        for text, data in combo_dict.items():
            w.addItem(text, data)

        w.setCurrentIndex(meta.get("default", 0))

    elif ptype is str and name == "path":   # if making a path widget
        w = PathStandardWidget(
            str(meta.get("default", "")),
            meta.get("label", "Browse"),
            mode=meta.get("mode", "file"),
        )

    else:
        raise TypeError(f"Unsupported parameter type: {ptype}")
    
    description = meta.get("description")
    if description:
        w.setToolTip(description)     # add a tool tip

    return w


def load_standard_widgets(layout: QGridLayout,
                          parameters: dict[str, dict],
                          *,
                          max_per_row: int = 6,
                          start_row: int = 0,
                          start_col: int = 0,) -> tuple[dict[str, QWidget], int, int]:
    '''
    Create and place parameter widgets in a given grid layout.

        Args:
            layout: (QGridLayout)
                the layout in which the parameters must be placed.
            
            parameters: (dict[str, dict])
                the parameters dictionary, containing a dictionary of
                default configurations for each parameter name.
            
            max_per_row: (int)
                the maximum number of element per row.
                (default 6)
        
        Returns:
            widgets: (dict[str, QWidget])
                the dictionary {param_name, widget} of the placed widgets.
    '''
    items: list[tuple[str, QWidget]] = []    # list of (label, widget) to place in the layout
    widgets: dict[str, QWidget] = {}         # dict{param_name: widget}

    for name, meta in parameters.items():        # for each parameter
        w = create_standard_widget(name, meta)   # create the corresponding widget
        label = meta.get("label", name)          # create the label to use (default is param name)

        items.append((label, w))  # add the tuple (label, widget) in the list
        widgets[name] = w         # add the widget in the dictionary

    # place the widget in the layout
    row, col = place_labeled_widgets(
        layout,
        items,
        max_per_row=max_per_row,
        start_row=start_row,
        start_col=start_col
    )

    return widgets, row, col
