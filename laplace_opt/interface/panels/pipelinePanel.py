# libraries
from PyQt6.QtWidgets import (
    QGroupBox, QGridLayout, QComboBox,
)
from PyQt6.QtCore import pyqtSignal
from laplace_log import log

# project
from ...utils.getter import get_classes
from ...utils.standard_widgets import place_labeled_widgets
from ...utils.config_helper import get_from_config, set_in_config
from ...model_construction import (
    AcquisitionStructure, StrategyStructure
)

StratOrAcq = StrategyStructure | AcquisitionStructure


class PipelinePanel(QGroupBox):
    '''
    Panel enabling the selection of the optimization strategy and
    acquisition function.

    Read the available features in the corresponding folders using
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
            "strategy": ("Strategy", "strategies", "default_strategy_name"),
            "acquisition": ("Acquisition", "acquisitions", "default_acquisition_name"),
        }
        # for each stage, there is a dictionary of the corresponding classes
        self.classes: dict[str, dict[str, StratOrAcq]] = {}
        self.combos: dict[str, QComboBox] = {} # for each stage, there is a combo box

        self.set_up()  # build the widgets

        # define the default combo box selection for each stage
        for stage, combo in self.combos.items():
            # get the default combo box selection for this stage
            title, _, default_in_config = self.stages[stage]
            default_name = get_from_config(
                module="interface", 
                item=default_in_config, 
                default_value="", 
                type=str
            )
            # for each stage class
            for index, cls_name in enumerate(self.classes[stage].keys()):
                if cls_name == default_name:  # if the class is the default one
                    if index > 0:             # and the selection not already valid
                        combo.setCurrentIndex(index)  # set the current selection
                    else:
                        log.info(f"New {title} selected: '{cls_name}'") # else print the selection in logs


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
        for stage, (title, category, default_in_config) in self.stages.items():

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
            combo.currentIndexChanged.connect(
                lambda index, *, stage=stage: self.on_current_index_changed(
                    index=index,
                    stage=stage
                )
            )

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


    def on_current_index_changed(self, index: int, stage: str) -> None:
        '''When a combo box is changed, emit a signal and indicate it in the logs'''        
        # get stage information
        title, category, default_in_config = self.stages[stage]
        # get the class name selected
        val = list(self.classes[stage].keys())[index]
        
        # set the new default in config
        set_in_config(
            module="interface",
            item=default_in_config,
            val=val
        )

        log.info(f"New {title} selected: '{val}'")

        self.selection_changed.emit()  # emit the signal


    ### helpers

    def get_selection(self) -> dict[str, StratOrAcq]:
        '''
        Return the selected classes for each stage.
        '''
        result = {}
        for stage, combo in self.combos.items():
            key = combo.currentData()
            result[stage] = self.classes[stage][key]
        return result
