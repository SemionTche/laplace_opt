# libraries
from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QComboBox, QWidget, 
    QSpinBox, QGridLayout, QDoubleSpinBox
)

from log_laplace.log_lhc import log

# project
from utils.getter import get_classes
from utils.standard_widgets import load_standard_widgets
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
        default_init = 1
        self.selector.setCurrentIndex(default_init)
        self.update_parameters(default_init)    # create the parameter widget


    def actions(self) -> None:
        '''
        Define the actions of the initialization panel.
        '''
        # when a new initialization is selected, update the parameter widgets
        self.selector.currentIndexChanged.connect(self.update_parameters)


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

    def get_initialization(self) -> dict[str, dict[InitializationStructure, dict[str, int, float, bool]]]:
        cls = list(self.init_cls.values())[self.selector.currentIndex()]
        params = {}

        for k, w in self.param_widgets.items():
            if isinstance(w, QSpinBox | QDoubleSpinBox):
                params[k] = w.value()
            elif isinstance(w, QComboBox):
                params[k] = (w.currentIndex() == 0)
            else:
                params[k] = w.text()

        return {"cls": cls, "params": params}