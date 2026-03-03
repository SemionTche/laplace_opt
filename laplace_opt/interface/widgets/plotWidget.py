# libraries
from copy import deepcopy

from laplace_log import log
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QPushButton, QCheckBox
)
from PyQt6.QtCore import pyqtSignal

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class PlotWidget(QWidget):
    '''
    Widget responsible for displaying a single optimization plot.

    The PlotWidget provides interactive selection of X and Y variables,
    optional logarithmic scaling, and dynamic visualization of data
    updates. Newly added data points are highlighted to distinguish
    them from previously displayed values.

    The widget maintains an internal copy of the current and previous
    data states in order to detect incremental updates.
    '''

    delete_requested = pyqtSignal(object)

    def __init__(self, available_keys: list[str]):
        '''
        Initialize the PlotWidget.

        Arg:
            available_keys: (list[str])
                List of variable names that can be selected for the X and Y axes.
        '''
        super().__init__()

        self.available_keys = available_keys
        
        self.set_up()
        self.actions()

        self._data: dict[str, list] = {}
        self._data_old: dict[str, list] = {}

        log.debug("Plot widget created.")


    def set_up(self) -> None:
        '''
        Construct and arrange the user interface elements.

        This method creates the axis selectors, logarithmic scale controls,
        deletion button, and the embedded Matplotlib canvas.
        '''
        # layout
        main_layout = QVBoxLayout(self)

        # Controls row
        controls = QHBoxLayout()

        # combo box choosing the x values
        self.x_selector = QComboBox()
        self.x_selector.addItems(self.available_keys)

        # combo box choosing the y values
        self.y_selector = QComboBox()
        self.y_selector.addItems(self.available_keys)

        # log checkboxes
        self.log_X = QCheckBox("Log X")
        self.log_Y = QCheckBox("Log Y")

        # delete button
        self.delete_button = QPushButton("Delete plot")

        # adding widgets to the layout
        controls.addWidget(self.x_selector)
        controls.addWidget(self.y_selector)
        controls.addWidget(self.log_X)
        controls.addWidget(self.log_Y)
        controls.addWidget(self.delete_button)

        main_layout.addLayout(controls)

        # Matplotlib Figure
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        main_layout.addWidget(self.canvas)


    def actions(self) -> None:
        '''
        Connect widget signals to their corresponding callbacks.

        Axis selection changes and scale toggles trigger a redraw of the plot.
        The delete button emits the delete_requested signal.
        '''
        self.delete_button.clicked.connect(
            lambda: self.delete_requested.emit(self)
        )

        # when selecting one of the following element, redraw the plot
        self.x_selector.currentTextChanged.connect(self._redraw)
        self.y_selector.currentTextChanged.connect(self._redraw)
        self.log_Y.stateChanged.connect(self._redraw)
        self.log_X.stateChanged.connect(self._redraw)


    def update_plot_dict(self, data_dict: dict[str, list]) -> None:
        '''
        Update the internal data and refresh the visualization.

        Arg:
            data_dict: (dict[str, list])
                Mapping of variable names to ordered lists of values.
                A deep copy is stored internally to allow comparison with
                the previous state and identification of newly added points.
        '''
        self._data_old = deepcopy(self._data)
        self._data = deepcopy(data_dict)
        self._redraw()


    def _redraw(self) -> None:
        '''
        Redraw the plot using the currently selected variables.

        Previously existing data points are rendered in blue, while
        newly appended points are rendered in red. Axis labels and
        logarithmic scaling options are applied according to the
        current widget state.
        '''
        self.figure.clear()                     # clear the previous figure
        ax = self.figure.add_subplot(111)       # make an axis

        if not self._data:
            self.canvas.draw()                  # if there is no data, keep it white
            return

        x_key = self.x_selector.currentText()   # get the current keys
        y_key = self.y_selector.currentText()

        if x_key not in self._data or y_key not in self._data:     # if the keys are not in the data dict
            self.canvas.draw()                                     # keep it white
            return

        x = self._data[x_key]      # get the data associated to the key
        y = self._data[y_key]

        ax.set_xlabel(x_key)       # set labels
        ax.set_ylabel(y_key)

        if not x or not y:         # if there is no data
            self.canvas.draw()     # keep it white
            return

        old_len = len(self._data_old.get(x_key, []))
        new_len = len(x)
        old_len = min(old_len, new_len)   # compare old length and new length and consider the lower as 'old'
        
        x_old = x[:old_len]     # extract the corresponding data
        y_old = y[:old_len]

        x_new = x[old_len:]
        y_new = y[old_len:]

        if x_old and y_old:
            ax.scatter(x_old, y_old, s=80, 
                       marker="o", ec="black", color="tab:blue")   # plot the old data
        
        if x_new and y_new:
            ax.scatter(x_new, y_new, s=80, 
                       marker="o", ec="black", color="red")        # plot the new data

        if self.log_X.isChecked():          # if log scale, apply it
            ax.set_xscale("log")
        if self.log_Y.isChecked():
            ax.set_yscale("log")

        self.canvas.draw()
    

    def set_available_keys(self, keys: list[str]) -> None:
        '''
        Update the list of selectable variables for both axes.

        Arg:
            keys: (list[str])
                New set of variable names to populate the X and Y selectors.

        Signals are temporarily blocked to prevent unnecessary redraws
        during the update.
        '''
        self.x_selector.blockSignals(True)   # bloc the combo box signals
        self.y_selector.blockSignals(True)

        self.x_selector.clear()              # clear the current keys
        self.y_selector.clear()

        self.x_selector.addItems(keys)       # set the new one
        self.y_selector.addItems(keys)

        self.x_selector.blockSignals(False)  # unblock the signals
        self.y_selector.blockSignals(False)
