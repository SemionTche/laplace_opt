from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QRadioButton,
    QWidget, QLabel, QSpinBox, QDoubleSpinBox
)
from utils.getter import get_classes


class RadioStagePanel(QGroupBox):
    def __init__(self, title: str, category: str):
        super().__init__(title)

        self.layout = QVBoxLayout(self)
        self.buttons = {}
        self.param_widgets = {}
        self.param_panels = {}

        self.classes = get_classes(category)

        for i, (name, cls) in enumerate(self.classes.items()):
            btn = QRadioButton(cls.display_name)
            self.layout.addWidget(btn)
            self.buttons[name] = btn

            panel = QWidget()
            panel_layout = QVBoxLayout(panel)

            widgets = {}
            for pname, meta in cls.parameters.items():
                panel_layout.addWidget(QLabel(pname))

                if meta["type"] is int:
                    w = QSpinBox()
                    w.setValue(meta["default"])
                else:
                    w = QDoubleSpinBox()
                    w.setDecimals(6)
                    w.setValue(meta["default"])

                panel_layout.addWidget(w)
                widgets[pname] = w

            panel.setVisible(False)
            self.layout.addWidget(panel)

            self.param_panels[name] = panel
            self.param_widgets[name] = widgets

            btn.toggled.connect(
                lambda checked, n=name: self._toggle(n, checked)
            )

            if i == 0:
                btn.setChecked(True)

    def _toggle(self, name, checked):
        self.param_panels[name].setVisible(checked)

    def get_selection(self):
        for name, btn in self.buttons.items():
            if btn.isChecked():
                cls = self.classes[name]
                params = {
                    k: w.value()
                    for k, w in self.param_widgets[name].items()
                }
                return cls(), params