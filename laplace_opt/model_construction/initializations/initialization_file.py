# libraries
from pathlib import Path

from laplace_log import log
import torch

# project
from laplace_opt.model_construction.initializations.initialization_structure import InitializationStructure


class FileInitialization(InitializationStructure):
    display_name = "Load from file"
    description = "Load initial points from a file"

    parameters = {
        "path": {
            "type": str,
            "mode": "file",
            "default": "",
            "label": "File path",
            "description": "Use already sampled data"
        }
    }

    def generate(self, bounds, path: str):
        checkpoint = torch.load(Path(path))
        try:
            X: torch.Tensor = checkpoint["observations"]["X_physical"]
            Y: torch.Tensor = checkpoint["observations"]["Y_physical"]
            return X.double(), Y.double()
        except Exception as e:
            log.error(f"Error: {e}\nCould not read X or Y from the given file.")
            return None, None
