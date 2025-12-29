from PyQt6.QtWidgets import (
    QGroupBox, QGridLayout
)

from utils.standard_widgets import load_standard_widgets

class HyperparameterPanel(QGroupBox):
    def __init__(self):
        super().__init__("Hyperparameters")
        self.layout = QGridLayout(self)
        self.widgets = {}

    def clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.widgets.clear()

    def load_from_classes(self, classes: list[type]):
        self.clear()

        for cls in classes:
            widgets = load_standard_widgets(
                self.layout,
                cls.parameters,
                max_per_row=6,
            )
            for name, w in widgets.items():
                self.widgets[(cls, name)] = w


    def get_parameters(self):
        result = {}
        for (cls, name), widget in self.widgets.items():
            result.setdefault(cls, {})[name] = widget.value()
        return result
