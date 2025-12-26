from PyQt6.QtWidgets import (
    QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox
)


class HyperparameterPanel(QGroupBox):
    def __init__(self):
        super().__init__("Hyperparameters")
        self.layout = QFormLayout(self)
        self.widgets = {}

    def clear(self):
        while self.layout.count():
            self.layout.removeRow(0)
        self.widgets.clear()

    def load_from_classes(self, classes: list[type]):
        self.clear()

        for cls in classes:
            for name, meta in cls.parameters.items():
                if meta["type"] is int:
                    w = QSpinBox()
                    w.setValue(meta["default"])
                else:
                    w = QDoubleSpinBox()
                    w.setDecimals(6)
                    w.setValue(meta["default"])

                self.layout.addRow(f"{cls.display_name} — {name}", w)
                self.widgets[(cls, name)] = w

    def get_parameters(self):
        result = {}
        for (cls, name), widget in self.widgets.items():
            result.setdefault(cls, {})[name] = widget.value()
        return result
