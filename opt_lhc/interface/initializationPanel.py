# libraries
from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QComboBox, QWidget, 
    QSpinBox, QGridLayout, QDoubleSpinBox
)

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

        # when a new initialization is selected, update the parameter widget
        self.selector.currentIndexChanged.connect(self.update_parameters)


    def set_up(self) -> None:
        '''
        Function made to create and set the widgets
        of the InitializationPanel class.
        '''
        # main init
        init_layout = QVBoxLayout(self)
        
        # combo box
        self.selector = QComboBox()
        init_layout.addWidget(self.selector)

        # parameters
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
        self.update_parameters(default_init) # create the parameter widget


    def update_parameters(self, index: int) -> None:
        '''
        Change the parameter widget depending on the selected 
        initialization. 'index' indicates the item selected.
        '''
        # clear old widgets
        while self.param_layout.count():
            item = self.param_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # get the corresponding init class
        cls = list(self.init_cls.values())[index]

        # get the class parameters
        parameters = cls.get_parameters()

        # dictionary that will contained every parameter widget
        self.param_widgets = load_standard_widgets(
            self.param_layout,
            parameters,
            max_per_row=6,
        )

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