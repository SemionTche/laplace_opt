from PyQt6.QtWidgets import (
    QWidget,
    QFormLayout,
    QDoubleSpinBox,
)
from PyQt6.QtCore import pyqtSignal


class SliceWidget(QWidget):

    slice_changed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self.layout = QFormLayout(self)
        self.spinboxes = {}


    def set_slice(self, input_list: list[str], x_axis: str, bounds):
        old_values = {
            name: spin.value()
            for name, spin in self.spinboxes.items()
        }

        self.spinboxes.clear()

        # clear previous rows
        while self.layout.rowCount():
            self.layout.removeRow(0)

        self.spinboxes.clear()

        for (name, bd) in zip(input_list, bounds.T):
            print(f"name = {name}, bounds = {bd}")
            if name == x_axis:
                continue

            spin = QDoubleSpinBox()
            spin.setRange(float(bd[0]), float(bd[1]))
            step = (bd[1] - bd[0]) / (n_per_dim - 1)        # need to pass the model_sample
            spin.setDecimals(float(step))
            if name in old_values:
                spin.setValue(old_values[name])
            else:
                idx = round((bd.mean() - bd[0]) / step)
                value = bd[0] + idx * step
                spin.setValue(float(value))

            spin.valueChanged.connect(self._emit_slice)

            self.layout.addRow(name, spin)
            self.spinboxes[name] = spin


    def _emit_slice(self):
        self.slice_changed.emit(
            {
                name: spin.value()
                for name, spin in self.spinboxes.items()
            }
        )

    def get_slice(self):
        return {
            name: spin.value()
            for name, spin in self.spinboxes.items()
        }