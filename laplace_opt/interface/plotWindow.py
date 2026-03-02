# libraries
import pathlib

import qdarkstyle
from laplace_log import log
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QGridLayout, QMessageBox
)
from PyQt6.QtGui import QIcon

# project
from .widgets import PlotWidget


class PlotWindow(QWidget):
    '''
    A window widget for live visualization of optimization results.

    The PlotWindow manages multiple PlotWidget instances in a grid layout,
    allowing the user to monitor the evolution of inputs and objectives
    during an optimization process. It supports dynamic addition and removal
    of plots, automatic updates when new results are received, and selection
    of variables for the X and Y axes.
    '''
    MAX_ROWS = 3
    MAX_COLS = 4

    def __init__(self):
        '''
        Initialize the PlotWindow instance.

        Sets up the GUI, including the "+" button for adding new plots
        and the grid layout for displaying PlotWidget instances. Initializes
        internal state for available keys, stored data, and active plots.
        '''
        super().__init__() # heritage from QWidget

        self.available_keys = [""]            # inputs and objectives availables
        self.plots: list[PlotWidget] = []     # list of plot widget displayed

        self.set_up()      # set the layout
        self.actions()     # set the actions


    def set_up(self) -> None:
        '''
        Configure the window layout and appearance.

        Sets the window title, size, icon, stylesheet, and initializes
        the main vertical layout containing the "+" button and the plot grid.
        '''
        p = pathlib.Path(__file__)

        # window
        self.setWindowTitle("Live Optimization Plot")
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        self.setGeometry(120, 30, 1000, 700)

        # icon
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
        '''
        Connect widget signals to their corresponding actions.
        '''
        # when the add button is clicked, use the add_plot method
        self.add_button.clicked.connect(
            self.add_plot
        )


    def add_plot(self) -> None:
        '''
        Add a new PlotWidget to the window.

        Creates a PlotWidget using the currently available keys, connects
        its deletion signal, appends it to the list of plots, and refreshes
        the grid layout. Does nothing if the maximum number of plots is reached.
        '''
        if len(self.plots) >= self.MAX_ROWS * self.MAX_COLS:  # if there are more plots than expected
            QMessageBox.warning(                              # show a warning box
                self, 
                "Limit reached",
                "Maximum number of plots reached."
            )
            return                                            # ignore the action

        plot = PlotWidget(self.available_keys)                # else add a plot widget
        plot.delete_requested.connect(self.remove_plot)       # set the remove option in the PlotWidget
        
        plot.update_plot_dict(self.data)   # set the current data
        self.plots.append(plot)            # add the plot widget in the list
        self._refresh_grid()               # refresh the display
        log.debug("Plot widget added.")


    def remove_plot(self, plot_widget: PlotWidget) -> None:
        '''
        Remove a PlotWidget from the window.

        Arg:
            plot_widget: (PlotWidget)
                The plot widget to be removed. The widget is deleted
                and the grid layout is refreshed.
        '''
        # remove a plot widget
        self.plots.remove(plot_widget)
        plot_widget.setParent(None)
        plot_widget.deleteLater()

        self._refresh_grid()  # refresh the display
        log.debug("Plot widget removed.")


    def _refresh_grid(self) -> None:
        '''
        Reorganize the PlotWidget grid layout.

        Clears the current grid layout and re-adds all PlotWidgets
        according to their current order, respecting MAX_COLS.
        '''
        # Clear the grid
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().setParent(None)

        # Re-add properly
        for index, plot in enumerate(self.plots):
            row = index // self.MAX_COLS
            col = index % self.MAX_COLS
            self.grid.addWidget(plot, row, col)
        log.debug("Plot window refreshed.")


    def add_result(self, result_list: list[dict]) -> None:
        '''
        Update internal data with new optimization results.

        Arg:
            result_list: (list of dict)
                List of result dictionaries from the optimizer. Each dictionary
                must contain 'inputs' and 'outputs' mappings. Data is extracted
                using input_map and objective_map metadata and appended to the
                corresponding lists in self.data. Notifies all PlotWidgets
                to refresh their visualization.
        '''
        for result in result_list:  # for each measure
            
            # Inputs
            inputs = result.get("inputs", {})
            for display_name, meta in self.input_map.items():   # for each input
                
                address = meta["address"]       # get the address
                position = meta["position"]     # get the position index

                if address in inputs:         # if the address is in the inputs
                    values = inputs[address]  # get the values 

                    if position < len(values):
                        self.data[display_name].append(values[position])    # add the position index in the corresponding list

            # Objectives
            outputs = result.get("outputs", {})
            for display_name, meta in self.objective_map.items():  # for each objective

                address = meta["address"]      # get the address
                key = meta["key"]              # get the objective key

                if address in outputs:          # if the address is in the objectives
                    payload = outputs[address]  # get the values

                    if key in payload:            # if the key is in the values
                        value = payload[key][0]
                        self.data[display_name].append(value)   # add the value in the corresponding list

        self.data["iteration"] = range(len(self.data[display_name]))    # make an iteration list

        for plot in self.plots:                 # for each plot
            plot.update_plot_dict(self.data)    # update the current data

        
    def configure_from_form(self, form: dict) -> None:
        '''
        Reset the plotting window using a new optimization form.

        Arg:
            form: (dict)
                The optimization form dictionary containing inputs and objectives.
                Extracts input and objective variable metadata and initializes
                data containers for plotting. Clears any existing plots and
                updates the available_keys list.
        '''
        # Clear data and plot list
        self.data = {}
        self.plots.clear()

        # Clear the grid
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().setParent(None)

        self.input_map = {}
        self.objective_map = {}

        # Inputs
        inputs_dict = form.get("inputs", {})
        for display_name, input in inputs_dict.items():   # for each input (display name is the name of the class)

            ip_port = input.address             # get the address
            position = input.position_index     # get the position index

            self.input_map[display_name] = {    # make the input mapping
                "address": ip_port,
                "position": position
            }

            self.data[display_name] = []  # set the data list for this input

        # Objectives
        objectives = form.get("obj", {})
        for display_name, obj_obj in objectives.items():  # for each objective

            ip_port = obj_obj.address           # get the address
            output_key = obj_obj.output_key     # get the key

            self.objective_map[display_name] = {    # make the objective mapping
                "address": ip_port,
                "key": output_key
            }

            self.data[display_name] = []    # set the data list of this objective
        
        self.data["iteration"] = []    # set the iteration list
        
        self.available_keys = list(self.data.keys())    # define the available keys for the plot widgets
        log.debug(f"PlotWindow configured with keys: {self.available_keys}")