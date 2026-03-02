# libraries
import copy
from laplace_log import log
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QPushButton, QCheckBox
)
from PyQt6.QtCore import pyqtSignal

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class PlotWidget(QWidget):

    delete_requested = pyqtSignal(object)

    def __init__(self, available_keys):
        super().__init__()

        self.available_keys = available_keys

        main_layout = QVBoxLayout(self)

        # ---- Controls row ----
        controls = QHBoxLayout()

        self.x_selector = QComboBox()
        self.x_selector.addItems(self.available_keys)

        self.y_selector = QComboBox()
        self.y_selector.addItems(self.available_keys)

        self.log_X = QCheckBox("Log X")
        self.log_Y = QCheckBox("Log Y")

        self.delete_button = QPushButton("Delete plot")

        controls.addWidget(self.x_selector)
        controls.addWidget(self.y_selector)
        controls.addWidget(self.log_X)
        controls.addWidget(self.log_Y)
        controls.addWidget(self.delete_button)

        main_layout.addLayout(controls)

        # ---- Matplotlib Figure ----
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        main_layout.addWidget(self.canvas)

        # Connections
        self.delete_button.clicked.connect(
            lambda: self.delete_requested.emit(self)
        )

        self.x_selector.currentTextChanged.connect(self._redraw)
        self.y_selector.currentTextChanged.connect(self._redraw)
        self.log_Y.stateChanged.connect(self._redraw)
        self.log_X.stateChanged.connect(self._redraw)

        self._data: dict[str, list] = {}
        self._data_old: dict[str, list] = {}

    # -------------------------

    def update_plot_dict(self, data_dict: dict[str, list]):
        self._data_old = copy.deepcopy(self._data)
        self._data = copy.deepcopy(data_dict)
        self._redraw()


    def _redraw(self):

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if not self._data:
            self.canvas.draw()
            return

        x_key = self.x_selector.currentText()
        y_key = self.y_selector.currentText()

        if x_key not in self._data or y_key not in self._data:
            self.canvas.draw()
            return

        x = self._data[x_key]
        y = self._data[y_key]

        ax.set_xlabel(x_key)
        ax.set_ylabel(y_key)

        if not x or not y:
            self.canvas.draw()
            return
        

        old_len = len(self._data_old.get(x_key, []))
        new_len = len(x)
        old_len = min(old_len, new_len)
        
        x_old = x[:old_len]
        y_old = y[:old_len]

        x_new = x[old_len:]
        y_new = y[old_len:]

        if x_old and y_old:
            ax.scatter(x_old, y_old, s=80, marker="o", ec="black", color="tab:blue")
        
        if x_new and y_new:
            ax.scatter(x_new, y_new, s=80, marker="o", ec="black", color="red")

        if self.log_X.isChecked():
            ax.set_xscale("log")
        if self.log_Y.isChecked():
            ax.set_yscale("log")

        self.canvas.draw()
    

    def set_available_keys(self, keys: list[str]):

        self.x_selector.blockSignals(True)
        self.y_selector.blockSignals(True)

        self.x_selector.clear()
        self.y_selector.clear()

        self.x_selector.addItems(keys)
        self.y_selector.addItems(keys)

        self.x_selector.blockSignals(False)
        self.y_selector.blockSignals(False)
