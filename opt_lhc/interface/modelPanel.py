from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QCheckBox
from interface.pipelineSelectorPanel import PipelineSelectorPanel
from interface.hyperparameterPanel import HyperparameterPanel


class ModelPanel(QGroupBox):
    def __init__(self):
        super().__init__("Model")

        layout = QVBoxLayout(self)

        self.enable_checkbox = QCheckBox("Enable model-based optimization")
        self.enable_checkbox.setChecked(True)

        self.pipeline = PipelineSelectorPanel()
        self.hyperparams = HyperparameterPanel()

        layout.addWidget(self.enable_checkbox)
        layout.addWidget(self.pipeline)
        layout.addWidget(self.hyperparams)

        self.update_hyperparameters()

        self.enable_checkbox.toggled.connect(self._on_enabled)
        
        self.pipeline.selection_changed.connect(
            self.update_hyperparameters
        )


    def _on_enabled(self, enabled: bool):
        self.pipeline.setEnabled(enabled)
        self.hyperparams.setEnabled(enabled)

    def update_hyperparameters(self):
        if not self.enable_checkbox.isChecked():
            self.hyperparams.clear()
            return

        selected = self.pipeline.get_selection()
        self.hyperparams.load_from_classes(selected.values())

    def get_config(self):
        if not self.enable_checkbox.isChecked():
            return {"enabled": False, "classes": {}, "hyperparameters": {}}

        classes = self.pipeline.get_selection()
        hyperparams = self.hyperparams.get_parameters()

        return {
            "enabled": True,
            "classes": classes,
            "hyperparameters": hyperparams
        }

