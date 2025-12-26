from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QComboBox, QWidget, QLabel, QSpinBox, QLineEdit
)
from utils.getter import get_classes


class InitializationPanel(QGroupBox):
    def __init__(self):
        super().__init__("Initialization")

        self.layout = QVBoxLayout(self)
        self.selector = QComboBox()
        self.layout.addWidget(self.selector)

        self.param_widget = QWidget()
        self.param_layout = QVBoxLayout(self.param_widget)
        self.layout.addWidget(self.param_widget)

        self.classes = get_classes("initializations")
        self.selector.addItems(
            cls.display_name for cls in self.classes.values()
        )

        self.selector.currentIndexChanged.connect(self.update_parameters)
        self.update_parameters(0)

    def update_parameters(self, index: int):
        # clear old widgets
        while self.param_layout.count():
            self.param_layout.takeAt(0).widget().deleteLater()

        cls = list(self.classes.values())[index]
        self.param_widgets = {}

        for name, meta in cls.get_parameters().items():
            label = QLabel(meta.get("label", name))
            self.param_layout.addWidget(label)

            if meta["type"] is int:
                w = QSpinBox()
                w.setRange(meta.get("min", 0), meta.get("max", 10_000))
                w.setValue(meta["default"])
            else:
                w = QLineEdit(meta["default"])

            self.param_layout.addWidget(w)
            self.param_widgets[name] = w

    def get_initialization(self):
        cls = list(self.classes.values())[self.selector.currentIndex()]
        params = {
            k: w.value() if hasattr(w, "value") else w.text()
            for k, w in self.param_widgets.items()
        }
        return cls(), params
