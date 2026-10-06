# libraries
from PyQt6.QtWidgets import (
    QGroupBox, QGridLayout, 
    QCheckBox, QComboBox
)

# project
from ...model_construction import CriteriumStructure
from ...utils.standard_widgets import load_standard_widgets
from ...utils.getter import get_criterium_cls
from ...utils.model_source import ModelSource


class CriteriumPanel(QGroupBox):
    '''
    Panel used to configure the optimization end criterium. 
    
    The criterium parameters are loaded from criterium folder of the ModelSource.
    '''

    def __init__(self, source: ModelSource):
        ''' 
        Arg:
            source (ModelSource):
                Object storing the 'model_construction' folder 
                location from which the structure is loaded.
        '''
        super().__init__("End criterium")
        
        self.source = source

        # get the criterium class
        self.crit_cls: CriteriumStructure = get_criterium_cls(self.source)
        self.crit_cls = self.crit_cls()   # instanciate the criterium class

        self.widgets = {}   # dict of param widgets 
        self.set_up()


    def set_up(self) -> None:
        '''Build and configure the criterium panel.'''
        layout = QGridLayout()
        self.setLayout(layout)

        # build widgets
        self.widgets, row, col = load_standard_widgets(
            layout,
            self.crit_cls.parameters,
            max_per_row=6,
            start_row=1,
            start_col=0
        )

        # optimal checkbox
        self.optimal_chekbox = QCheckBox("Optimization criterium")
        self.optimal_chekbox.setChecked(False)
        self.optimal_chekbox.setEnabled(False)

        layout.addWidget(self.optimal_chekbox, row+2, 0)


    def get_criterium(self)-> dict:
        '''Return criterium parameters in a dictionary.'''
        criterium = {}

        for name, widget in self.widgets.items():

            if hasattr(widget, "value"):  # if there is a value to extract
                value = widget.value()    # get the value
            
            elif isinstance(widget, QComboBox):  # if it is a QComboBox
                value = widget.currentData()

            elif hasattr(widget, "text"):
                value = widget.text()

            else:   # drop other widgets
                continue

            criterium[name] = value

        # checkbox (special case, not in self.widgets)
        criterium["is_optimization_criterium"] = self.optimal_chekbox.isChecked()

        return criterium
