# libraries
from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QCheckBox
)

# project
from interface.panels.pipelinePanel import PipelinePanel
from interface.panels.hyperparameterPanel import HyperparameterPanel

from model_construction.strategies.strategy_structure import StrategyStructure
from model_construction.acquisitions.acquisition_structure import AcquisitionStructure

StratOrAcq = StrategyStructure | AcquisitionStructure


class OptPanel(QGroupBox):
    '''
    This panel containes two panels, the PipelinePanel,
    enabling the strategy and acquisition function choice and
    the HyperparameterPanel, updated depending on the active
    strategy and acquisition function, allowing to define the
    hyperparameters of the optimization.
    '''
    def __init__(self):
        super().__init__("Optimization Model")

        self.set_up()  # build the widgets

        self.update_hyperparameters() # set the hyperparameters

        self.actions()  # defines the actions of the panel


    def set_up(self) -> None:
        '''
        Build the widgets of the OptPanel class.
        A check box to enable / disable the widgets
        A PipelinePanel to decide the strategy / acq func
        A HyperparameterPanel to define the hyperparameters
        of the model.
        '''
        opt_layout = QVBoxLayout(self)

        # making a enbaling / disabling check box
        self.enable_checkbox = QCheckBox("Enable model-based optimization")
        self.enable_checkbox.setChecked(True)

        # creating the panels
        self.pipeline = PipelinePanel()
        self.hyperparams = HyperparameterPanel()

        # add the widgets to the layout
        opt_layout.addWidget(self.enable_checkbox)
        opt_layout.addWidget(self.pipeline)
        opt_layout.addWidget(self.hyperparams)


    def actions(self) -> None:
        '''
        Defines the actions of the OptPanel.
        '''
        # when the check box is changed, enable / disable the widgets
        self.enable_checkbox.toggled.connect(self.on_enabled)
        
        # when the selected strategy / acquisition function changed
        # update the hyperparameters available
        self.pipeline.selection_changed.connect(
            self.update_hyperparameters
        )


    def on_enabled(self, enabled: bool) -> None:
        '''
        Enable / disable the panels in OptPanel.
        '''
        self.pipeline.setEnabled(enabled)
        self.hyperparams.setEnabled(enabled)


    def update_hyperparameters(self) -> None:
        '''
        Update the HyperparameterPanel.
        '''
        # clear all widgets
        if not self.enable_checkbox.isChecked():
            self.hyperparams.clear()
            return

        selected = self.pipeline.get_selection() # get the current strategy / acq func
        self.hyperparams.load_from_classes(selected.values()) # load the corresponding widgets


    def get_opt(self) -> dict[str, bool | dict[str, dict[str, StratOrAcq | dict[str, int | float | bool | str]]]]:
        '''
        Return the OptPanel configuration, including a
        boolean 'enabled' to define if the OptPanel should be used.
        The pipeline key return a dictionary that provide for the
        'strategy' and 'acquisition' keys a dictionary with the class
        stored in 'cls' and the hyperparameters stored in 'params'.
        '''
        if not self.enable_checkbox.isChecked():      # if no optimization
            return {"enabled": False, "pipeline": {}} # get no pipeline

        pipeline_classes = self.pipeline.get_selection() # get the pipeline elements
        hyperparams = self.hyperparams.get_parameters()  # get the hyperparameter elements

        pipeline_cfg = {} # make the pipeline dictionary

        for stage, cls in pipeline_classes.items(): # for every stage
            pipeline_cfg[stage] = {                 # create a dictionary
                "cls": cls,                         # with the class
                "params": hyperparams.get(cls, {})  # and the parameters
            }

        return {"enabled": True, "pipeline": pipeline_cfg}
