# libraries
import pathlib
import qdarkstyle
from laplace_log import log
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QGridLayout, QMessageBox
)
from PyQt6.QtGui import QIcon

from .widgets import PlotWidget


class PlotWindow(QWidget):

    MAX_ROWS = 3
    MAX_COLS = 4


    def __init__(self):
        super().__init__()

        self.available_keys = [""]
        self.data = []
        self.plots = []

        self.set_up()
        self.actions()


    def set_up(self) -> None:
        p = pathlib.Path(__file__)

        self.setWindowTitle("Live Optimization Plot")
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        self.setGeometry(120, 30, 1000, 700)

        icon_path = p.parent / 'icons'
        self.setWindowIcon(QIcon(str(icon_path / 'LOA.png')))

        main_layout = QVBoxLayout(self)

        # "+" button
        self.add_button = QPushButton("+ Add Plot")
        main_layout.addWidget(self.add_button)

        # Grid for plots
        self.grid = QGridLayout()
        main_layout.addLayout(self.grid)


    def actions(self) -> None:
        self.add_button.clicked.connect(self.add_plot)


    def add_plot(self):

        if len(self.plots) >= self.MAX_ROWS * self.MAX_COLS:
            QMessageBox.warning(self, "Limit reached",
                                "Maximum number of plots reached.")
            return

        plot = PlotWidget(self.available_keys)
        plot.delete_requested.connect(self.remove_plot)
        plot.update_plot_dict(self.data)
        self.plots.append(plot)
        self._refresh_grid()


    def remove_plot(self, plot_widget) -> None:
        self.plots.remove(plot_widget)
        plot_widget.setParent(None)
        plot_widget.deleteLater()
        self._refresh_grid()


    def _refresh_grid(self):

        # Clear grid
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().setParent(None)

        # Re-add properly
        for index, plot in enumerate(self.plots):
            row = index // self.MAX_COLS
            col = index % self.MAX_COLS
            self.grid.addWidget(plot, row, col)


    def add_result(self, result_list: list[dict]):
        '''
        Receive raw optimizer results and normalize them.
        '''

        for result in result_list:

            # ------------------
            # Inputs
            # ------------------
            inputs = result.get("inputs", {})

            for display_name, meta in self.input_map.items():

                address = meta["address"]
                position = meta["position"]

                if address in inputs:
                    values = inputs[address]

                    if position < len(values):
                        self.data[display_name].append(values[position])

            # ------------------
            # Objectives
            # ------------------
            outputs = result.get("outputs", {})

            for display_name, meta in self.objective_map.items():

                address = meta["address"]
                key = meta["key"]

                if address in outputs:
                    payload = outputs[address]

                    if key in payload:
                        value = payload[key][0]   # objectives stored as list
                        self.data[display_name].append(value)

        self.data["iteration"] = range(len(self.data[display_name]))

        # After updating structured data → notify plots
        for plot in self.plots:
            plot.update_plot_dict(self.data)

        
    def configure_from_form(self, form: dict):
        '''
        Reset plotting window and extract structured metadata.
        '''

        # Clear data
        self.data = {}
        self.plots.clear()

        # Clear grid
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().setParent(None)

        self.input_map = {}
        self.objective_map = {}

        # ------------------
        # Inputs
        # ------------------
        inputs = form.get("inputs", {})

        for display_name, input_obj in inputs.items():

            # input_obj is your InputStructure instance
            ip_port = input_obj.address      # assuming property exists
            position = input_obj.position_index

            self.input_map[display_name] = {
                "address": ip_port,
                "position": position
            }

            self.data[display_name] = []

        # ------------------
        # Objectives
        # ------------------
        objectives = form.get("obj", {})

        for display_name, obj_obj in objectives.items():

            ip_port = obj_obj.address
            output_key = obj_obj.output_key

            self.objective_map[display_name] = {
                "address": ip_port,
                "key": output_key
            }

            self.data[display_name] = []
        
        self.data["iteration"] = []
        
        self.available_keys = list(self.data.keys())

        log.debug(f"PlotWindow configured with keys: {self.available_keys}")