# libraries
from PyQt6.QtWidgets import (
    QGroupBox, QGridLayout, QComboBox,
)
from PyQt6.QtCore import pyqtSignal

# project
from utils.getter import get_classes
from utils.standard_widgets import place_labeled_widgets


class PipelinePanel(QGroupBox):
    '''
    Panel enabling the selection of the optimization strategy and
    acquisition function.

    Read the available features in the respecting folders using
    'get_classes' import.
    '''
    # emit a signal when any combo box is changed
    selection_changed = pyqtSignal()

    def __init__(self):
        super().__init__("Pipeline") # heritage from QGroupBox
        
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

        items = []  # list of (label, widget) to be placed in the grid

        # for each stage (strategy, acquisition, ...)
        for stage, (title, category) in self.stages.items():

            # create the combo box
            combo = QComboBox()
            combo.setSizeAdjustPolicy(
                QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
            )

            # read the available classes
            cls_dict = get_classes(category)  # dict{class_names, classes}
            self.classes[stage] = cls_dict    # keep an acces to the classes

            # add an item in the combo box for each class
            for name, cls in cls_dict.items():
                combo.addItem(cls.display_name, userData=name)

            # emit a signal when any combo box is changed 
            combo.currentIndexChanged.connect(self.selection_changed.emit)

            self.combos[stage] = combo  # keep an acces to the combo box

            # store the (label, widget) pair for layout
            items.append((title, combo))

        # place the widgets with a maximum of 6 per row,
        # label on top and centered above the combo box
        place_labeled_widgets(
            self.model_layout,
            items,
            max_per_row=6,
        )

    ### helpers

    def get_selection(self) -> dict[str, type]:
        '''
        Return the selected classes for each stage.
        '''
        result = {}
        for stage, combo in self.combos.items():
            key = combo.currentData()
            result[stage] = self.classes[stage][key]
        return result
