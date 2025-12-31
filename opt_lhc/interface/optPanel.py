# libraries
from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QCheckBox
)

# project
from interface.pipelinePanel import PipelinePanel
from interface.hyperparameterPanel import HyperparameterPanel


class OptPanel(QGroupBox):
    '''
    Optimization Panel contained two panels, the PipelinePanel,
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


    def get_opt(self) -> dict[str, bool, dict]:
        '''
        Return the OptPanel configuration, including a
        boolean 'enabled' to define if the OptPanel should be used,
        and two dictionaries, one for the strategy, the other one for
        the hyperparameters.
        '''
        if not self.enable_checkbox.isChecked():
            return {"enabled": False, "pipeline": {}, "hyperparameters": {}}

        classes = self.pipeline.get_selection()
        hyperparams = self.hyperparams.get_parameters()

        return {
            "enabled": True,
            "pipeline": classes,
            "hyperparameters": hyperparams
        }