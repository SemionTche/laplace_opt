# libraries
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

        self.log_checkbox = QCheckBox("Log Y")

        self.delete_button = QPushButton("✕")
        self.delete_button.setFixedWidth(30)

        controls.addWidget(self.x_selector)
        controls.addWidget(self.y_selector)
        controls.addWidget(self.log_checkbox)
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
        self.log_checkbox.stateChanged.connect(self._redraw)

        self._data = []

    # -------------------------

    def update_plot_dict(self, data_dict: dict[str, list]):
        self._data = data_dict
        self._redraw()


    def _redraw(self):

        if not self._data:
            return

        x_key = self.x_selector.currentText()
        y_key = self.y_selector.currentText()

        if x_key not in self._data or y_key not in self._data:
            return

        x = self._data[x_key]
        y = self._data[y_key]

        if not x or not y:
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        ax.scatter(x, y, marker="o")

        if self.log_checkbox.isChecked():
            ax.set_yscale("log")

        ax.set_xlabel(x_key)
        ax.set_ylabel(y_key)

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
