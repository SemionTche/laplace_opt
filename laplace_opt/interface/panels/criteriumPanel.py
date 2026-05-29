from PyQt6.QtWidgets import (
    QGroupBox, QGridLayout, QCheckBox
)
from PyQt6.QtCore import Qt


from ...utils.standard_widgets import load_standard_widgets


class CriteriumPanel(QGroupBox):

    def __init__(self):
        super().__init__("End criterium")

        self.core = {
            "max_iterations": {
                "type": int,
                "default": 2,
                "min": 0,
                "max": 10_000,
                "label": "Max iterations",
                "description": "Maximum number of model iterations (init + opt).\n'0' meaning endless."
            },

            "n_repeats": {
                "type": int,
                "default": 2,
                "min": 1,
                "max": 1000,
                "label": "Number sample repeats",
                "description": "Number of repeated evaluations per candidate."
            },

            "save_period": {
                "type": int,
                "default": 1,
                "min": 0,
                "max": 100,
                "label": "Saving period",
                "description": (
                    "Number of optimization steps between automatic saves.\n"
                    "Set to '0' to disable."
                )
            },
        }

        self.widgets = {}
        self.set_up()


    def set_up(self) -> None:
        layout = QGridLayout()
        self.setLayout(layout)

        # build widgets
        self.widgets, row, col = load_standard_widgets(
            layout,
            self.core,
            max_per_row=6,
            start_row=1,
            start_col=0
        )

        # optimal checkbox
        self.optimal_chekbox = QCheckBox("Optimization criterium")
        self.optimal_chekbox.setChecked(False)
        self.optimal_chekbox.setEnabled(False)

        layout.addWidget(self.optimal_chekbox, row+2, 0)


    def get_criterium(self)-> dict:
        """
        Return all criterium values as a plain Python dictionary.
        """

        criterium = {}

        for name, widget in self.widgets.items():

            if hasattr(widget, "value"):  # if there is a value to extract
                value = widget.value()    # get the value
            
            elif isinstance(widget, QComboBox):  # if it is a QComboBox
                value = widget.currentData()

            elif hasattr(widget, "text"):
                value = widget.text()

            else:   # drop other widgets
                continue

            criterium[name] = value

        # checkbox (special case, not in self.widgets)
        criterium["is_optimization_criterium"] = self.optimal_chekbox.isChecked()

        return criterium
