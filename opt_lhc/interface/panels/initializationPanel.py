# libraries
from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QComboBox, QWidget, QLabel,
    QSpinBox, QGridLayout, QDoubleSpinBox, QLineEdit
)
from PyQt6.QtCore import QSettings

import pathlib

from log_laplace.log_lhc import log

# project
from utils.getter import get_classes
from utils.standard_widgets import load_standard_widgets
from utils.config_helper import get_from_config, set_in_config
from utils.path_standard_widget import PathStandardWidget

from model_construction.initializations.initialization_structure import InitializationStructure


class InitializationPanel(QGroupBox):
    '''
    Panel made to chose an initialization among those 
    available in 'model_configuration/initializations'.

    Create a combo box in order to select the initialization.
    Display the relevant hyperparameters of the init method
    such as the number of points or candidates.
    '''
    def __init__(self):

        super().__init__("Initialization") # heritage from QGroupBox

        self.init_cls: dict[str, InitializationStructure] = get_classes("initializations") # dict{class_name: class}

        self.set_up() # create and set the panel elements

        self.actions() # defines the panel actions


    def set_up(self) -> None:
        '''
        Function made to create and set the widgets
        of the InitializationPanel class.
        '''
        # init layout
        init_layout = QVBoxLayout(self)
        
        # combo box
        self.selector = QComboBox()
        init_layout.addWidget(self.selector)

        # parameter layout
        self.param_widget = QWidget()

        self.param_layout = QGridLayout(self.param_widget)
        self.param_layout.setHorizontalSpacing(12)
        self.param_layout.setVerticalSpacing(6)

        init_layout.addWidget(self.param_widget)

        # add an item in the selector for every initialization procedure
        self.selector.addItems(
            cls.display_name for cls in self.init_cls.values()
        )

        # get the default initialization structure
        default_init = get_from_config(
            module="interface", 
            item="default_initialization_name", 
            default_value="",
            type=str
        )
        
        if default_init:                                # if there is a default init
            for i, cls_name in enumerate(self.init_cls.keys()):  # for every init structure
                if cls_name == default_init:                     # if it's the default one
                    self.selector.setCurrentIndex(i)             # set the selector
                    self.update_parameters(i)                    # create the widgets
        else:
            self.update_parameters(0)                   # else the default is position 0


    def actions(self) -> None:
        '''
        Define the actions of the initialization panel.
        '''
        # when a new initialization is selected, update the parameter widgets
        self.selector.currentIndexChanged.connect(self.update_parameters)

        # when the new initialization is selected, update the config.ini default init
        self.selector.currentIndexChanged.connect(
            lambda index: set_in_config(
                module="interface",
                item="default_initialization_name",
                val=list(self.init_cls.keys())[index]
            )
        )


    def clear_param(self) -> None:
        '''
        Clear the widgets contained in the parameter layout
        '''
        while self.param_layout.count():        # while there are still widgets
            item = self.param_layout.takeAt(0)  # get the first param layout element
            if item.widget():                   # if it is a widget
                item.widget().deleteLater()     # delete it during next window loop
        log.debug("Initialization widget parameters cleared.")


    def update_parameters(self, index: int) -> None:
        '''
        Change the parameter widget depending on the selected 
        initialization. 'index' indicates the item selected.
        '''
        self.clear_param()  # clear the current param widgets

        # get the corresponding init class
        cls = list(self.init_cls.values())[index]

        log.debug(f"New initialization selected: '{cls.__name__}'")

        # get the class parameters
        parameters = cls.get_parameters()

        # create and place the parameter in the parameter layout
        # get a dictionary that will contained every parameter widget
        self.param_widgets, row, col = load_standard_widgets(
            self.param_layout,
            parameters,
            max_per_row=6,
        )
        log.debug("New initialization parameter widgets placed.")


    ### helpers

    def get_initialization(self) -> dict[str, InitializationStructure | dict[str, int | float | bool | str]]:
        '''
        Return the initialization dictionary indicating the chosen initialization structure
        along with the selected parameters.
        '''
        # get the current class
        cls = list(self.init_cls.values())[self.selector.currentIndex()]
        
        params: dict[str, int | float | bool | str] = {}

        for k, w in self.param_widgets.items():  # for every parameter widget
            
            if isinstance(w, QSpinBox | QDoubleSpinBox):  # if it is a value container
                params[k] = w.value()                     #     get the value
            
            elif isinstance(w, QComboBox):                # elif it is a QComboBox
                if w.currentText() in ["True", "False"]:  #     if it is a boolean QComboBox
                    params[k] = (w.currentIndex() == 0)   #          get the boolean value
            
            elif isinstance(w, (QLineEdit, QLabel, PathStandardWidget)):  # elif it is a text container
                params[k] = w.text()                                            # get the text

        return {"cls": cls, "params": params}