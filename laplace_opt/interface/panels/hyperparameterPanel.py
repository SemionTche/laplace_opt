# libraries
from PyQt6.QtWidgets import (
    QGroupBox, QGridLayout, 
    QWidget, QComboBox
)

from laplace_log import log

# project
from ...utils.standard_widgets import load_standard_widgets
from ...model_construction import (
    AcquisitionStructure, StrategyStructure
)

StratOrAcq = StrategyStructure | AcquisitionStructure


class HyperparameterPanel(QGroupBox):
    '''
    Panel displaying the available hyperparameters, depending on a
    class list given in 'load_from_classes'.
    '''
    def __init__(self):
        super().__init__("Hyperparameters")   # heritage from QGroupBox
        
        self.hyper_layout = QGridLayout(self) # main hyperparameter layout
        self.widgets: dict[tuple[StratOrAcq, str], QWidget] = {} # dict{(class, class_name): widget}


    def clear(self) -> None:
        '''
        Clear all widgets contained in the 'hyper_layout'.
        '''
        while self.hyper_layout.count():        # while there still is widget
            item = self.hyper_layout.takeAt(0)  # remove the item '0' from the layout and return it in item
            if item.widget():                   # if there is a widget
                item.widget().deleteLater()     # delete it (next event loop)
        self.widgets.clear()                    # clear the widgets dictionary

        log.debug("Hyperparameter widgets cleared.")


    def load_from_classes(self, classes: list[StratOrAcq]) -> None:
        '''
        Clear the current widgets and load the standard widgets of 
        the given 'classes' using there 'parameters' dictionay. 
        The function assumes that the classes respect the format, having 
        an attribute 'parameters': dict{param_name: config_dict}.
        '''
        self.clear()  # clear the current widgets
        row = 0
        col = 0

        for cls in classes:   # for every class
            
            # merge core_parameters (if present) and parameters
            if hasattr(cls, "core_parameters"):
                params = {**getattr(cls, "core_parameters", {}), **getattr(cls, "parameters", {})}
            else:
                params = getattr(cls, "parameters", {})

            widgets, row, col = load_standard_widgets(    # load the standard widgets
                self.hyper_layout,                        # in the 'hyper_layout'
                params,                                   # depending on it's parameter dictionary
                max_per_row=6,
                start_row=row,
                start_col=col
            )

            # update the widget dictionary
            for name, w in widgets.items():
                self.widgets[(cls, name)] = w  # tuple field (class, class_name): widget
        
        log.debug("Hyperparameter widgets loaded.")

    ### helpers

    def get_parameters(self) -> dict[StratOrAcq, dict[str, int | float | bool | str]] :
        '''
        Get a dictionary of the current hyperparameter widget values
        ordered as {class: {param_name: value}}.
        '''
        result: dict[type, dict[str, int | float | bool | str]] = {}

        for (cls, name), widget in self.widgets.items(): # for every param widget

            if hasattr(widget, "value"):  # if there is a value to extract
                value = widget.value()    # get the value
            
            elif isinstance(widget, QComboBox):  # if it is a QComboBox
                value = widget.currentData()

            elif hasattr(widget, "text"):
                value = widget.text()

            else:   # drop other widgets
                continue

            if cls not in result:  # if the class is not already in result
                result[cls] = {}   # create a dict{class: {}} in result

            result[cls][name] = value  # update the param value in result: dict{class: {param_name: value}}

        return result