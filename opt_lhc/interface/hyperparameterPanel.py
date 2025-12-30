# libraries
from PyQt6.QtWidgets import (
    QGroupBox, QGridLayout, 
    QWidget, QComboBox
)

# project
from utils.standard_widgets import load_standard_widgets


class HyperparameterPanel(QGroupBox):
    '''
    Docstring for HyperparameterPanel
    '''
    def __init__(self):
        super().__init__("Hyperparameters")   # heritage from QGroupBox
        
        self.hyper_layout = QGridLayout(self) # main hyperparameter layout
        self.widgets: dict[tuple[type, str], QWidget] = {} # dict{(class, class_name): widget}


    def clear(self) -> None:
        '''
        Clear all widgets contained in the 'hyper_layout'.
        '''
        while self.hyper_layout.count():        # while there still is widget
            item = self.hyper_layout.takeAt(0)  # remove the item '0' from the layout and return it in item
            if item.widget():                   # if there is a widget
                item.widget().deleteLater()     # delete it (next event loop)
        self.widgets.clear()                    # clear the widgets dictionary


    def load_from_classes(self, classes: list[type]) -> None:
        '''
        Clear the current widgets and load the standard widgets of 
        the given 'classes' using there 'parameters' dictionay. 
        The function assumes that the classes respect the format, having 
        an attribute 'parameters': dict{param_name: config_dict}.
        '''
        self.clear()  # clear the current widgets

        for cls in classes:   # for every class
            widgets = load_standard_widgets(    # load the standard widgets
                self.hyper_layout,              # in the 'hyper_layout'
                cls.parameters,                 # depending on it's parameter dictionary
                max_per_row=6,
            )

            # update the widget dictionary
            for name, w in widgets.items():
                self.widgets[(cls, name)] = w  # tuple field (class, class_name): widget

    ### helpers

    def get_parameters(self) -> dict[type, dict[str, float, int, bool]] :
        '''
        Get a dictionary of the current hyperparameter widget values
        ordered as {class: {param_name: value}}.
        '''
        result: dict[type, dict[str, float, int, bool]] = {}

        for (cls, name), widget in self.widgets.items(): # for every param widget

            if hasattr(widget, "value"):  # if there is a value to extract
                value = widget.value()    # get the value
            
            elif isinstance(widget, QComboBox):  # if it is a QComboBox
                if widget.currentText() in ["True", "False"]:  # checking for "True" or "False"
                    value = widget.currentIndex() == 0   # the value is "True" if "True is selected" else otherwise
            
            else:   # drop other widgets
                continue

            if cls not in result:  # if the class is not already in result
                result[cls] = {}   # create a dict{class: {}} in result

            result[cls][name] = value  # update the param value in result: dict{class: {param_name: value}}

        return result