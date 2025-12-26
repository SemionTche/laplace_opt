from PyQt6.QtWidgets import (
    QGroupBox, QGridLayout, QRadioButton, QLabel, QButtonGroup
)
from PyQt6.QtCore import pyqtSignal

from utils.getter import get_classes


class PipelineSelectorPanel(QGroupBox):

    selection_changed = pyqtSignal()

    def __init__(self):
        super().__init__("Model pipeline")

        self.layout = QGridLayout(self)

        self.stages = {
            "model": ("Model", "models"),
            "fitter": ("Fitter", "fitters"),
            "acquisition": ("Acquisition", "acquisitions"),
            "sampler": ("Sampler", "samplers"),
        }

        self.classes = {}
        self.buttons = {}
        self.groups = {}  # ✅ one button group per column

        # --- headers ---
        for col, (stage, (title, _)) in enumerate(self.stages.items()):
            self.layout.addWidget(QLabel(title), 0, col)

        # --- load classes ---
        max_rows = 0
        for stage, (_, category) in self.stages.items():
            cls_dict = get_classes(category)
            self.classes[stage] = cls_dict
            max_rows = max(max_rows, len(cls_dict))

        # --- create radio buttons ---
        for col, stage in enumerate(self.stages):
            self.groups[stage] = QButtonGroup(self)
            self.groups[stage].setExclusive(True)

            cls_list = list(self.classes[stage].items())

            for row, (name, cls) in enumerate(cls_list):
                btn = QRadioButton(cls.display_name)
                self.layout.addWidget(btn, row + 1, col)

                self.groups[stage].addButton(btn)
                self.buttons.setdefault(stage, {})[name] = btn

                if row == 0:
                    btn.setChecked(True)

                btn.toggled.connect(
                    lambda checked, s=stage: checked and self.selection_changed.emit()
                )


    def _emit_selection_changed(self):
        self.selection_changed.emit()


    def get_selection(self):
        result = {}
        for stage, btns in self.buttons.items():
            for name, btn in btns.items():
                if btn.isChecked():
                    result[stage] = self.classes[stage][name]
        return result
