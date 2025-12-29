# libraries
from PyQt6.QtWidgets import (
    QGroupBox,
    QGridLayout,
    QLabel,
    QComboBox,
)
from PyQt6.QtCore import pyqtSignal, Qt

# project
from utils.getter import get_classes


class ModelPanel(QGroupBox):
    '''
    Panel enabling the selection of the optimization strategy and
    acquisition function.

    Read the available features in the respecting folders using
    'get_classes' import.
    '''
    # emit a signal when any combo box is changed
    selection_changed = pyqtSignal()

    def __init__(self):
        super().__init__("Models") # heritage from QGroupBox
        
        # dictionary representing a tuple per column
        # the first element is the title, the second the folder
        # in which the classes must be read
        self.stages = {
            "strategy": ("Strategy", "strategies"),
            "acquisition": ("Acquisition", "acquisitions"),
        }

        self.classes: dict[str, dict] = {} # for each stage, there is a dictionary of the corresponding classes
        self.combos: dict[str, QComboBox] = {} # for each stage, there is a combo box

        self.set_up()  # build the widgets


    def set_up(self) -> None:
        '''
        Build the widgets of the ModelPanel class.
        One label and one combo box for the strategy
        and the acquisition function.
        '''
        self.model_layout = QGridLayout(self)
        self.model_layout.setHorizontalSpacing(20)

        # headers
        for col, (stage, (title, _)) in enumerate(self.stages.items()):
            label = QLabel(title)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.model_layout.addWidget(label, 0, col)

        # combo boxes
        for col, (stage, (_, category)) in enumerate(self.stages.items()):
            combo = QComboBox()
            combo.setSizeAdjustPolicy(
                QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
            )

            cls_dict = get_classes(category) # dict{class_names, classes}
            self.classes[stage] = cls_dict   # keep an acces to the classes

            for name, cls in cls_dict.items():  # for each class
                combo.addItem(cls.display_name, userData=name) # add an item in the combo box

            # emit a signal when any combo box is changed 
            combo.currentIndexChanged.connect(self.selection_changed.emit)

            self.combos[stage] = combo  # keep an acces to the combo box
            self.model_layout.addWidget(combo, 1, col)  # add the widget to the layout

    ### helpers

    def get_selection(self) -> dict[str, type]:
        '''
        Return selected classes for each stage.
        '''
        result = {}
        for stage, combo in self.combos.items():
            key = combo.currentData()
            result[stage] = self.classes[stage][key]
        return result
