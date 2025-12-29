# libraries
from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QComboBox, QWidget, QLabel, 
    QSpinBox, QLineEdit, QGridLayout, QDoubleSpinBox
)
from PyQt6.QtCore import Qt

# project
from interface.pathSelectorWidget import PathSelectorWidget
from utils.getter import get_classes


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

        self.init_cls = get_classes("initializations") # dict{class_name: class}

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

        cls = list(self.init_cls.values())[index] # get the corresponding init class
        parameters = cls.get_parameters() # get the class parameters

        self.param_widgets = {} # dictionary that will contained every parameter widget

        # grid structure
        max_per_row = 6 # max number of column
        col = 0
        base_row = 0

        for name, meta in parameters.items():
            if col >= max_per_row:
                col = 0
                base_row += 2  # if the column are full change the line

            # label
            label = QLabel(meta.get("label", name))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setToolTip(meta.get("description", ""))  # add description
            self.param_layout.addWidget(label, base_row, col)

            # widget
            if meta["type"] is int:
                w = QSpinBox()
                w.setRange(meta.get("min", 1), meta.get("max", 10_000))
                w.setValue(meta.get("default", 1))

            elif meta["type"] is float:
                w = QDoubleSpinBox()
                w.setDecimals(meta.get("decimals", 3))
                w.setSingleStep(meta.get("step", 0.1))
                w.setRange(meta.get("min", -1e9), meta.get("max", 1e9))
                w.setValue(meta.get("default", 0.))
            
            elif meta["type"] is bool:
                w = QComboBox()
                w.addItems(["True", "False"])
                default = meta.get("default", False)
                w.setCurrentIndex(0 if default else 1)

            elif meta["type"] is str and name == "path":
                w = PathSelectorWidget(
                    str(meta.get("default", "")), 
                    "Init Browse", 
                    mode="file"
                )

            self.param_layout.addWidget(w, base_row + 1, col)
            self.param_widgets[name] = w

            col += 1


    ### helpers

    def get_initialization(self):
        cls = list(self.init_cls.values())[self.selector.currentIndex()]
        params = {}

        for k, w in self.param_widgets.items():
            if isinstance(w, QSpinBox | QDoubleSpinBox):
                params[k] = w.value()
            elif isinstance(w, QComboBox):
                params[k] = (w.currentIndex() == 0)
            else:
                params[k] = w.text()

        return cls(), params

