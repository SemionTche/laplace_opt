import torch
import json
from pathlib import Path

from model_construction.initializations.initialization_structure import InitializationStructure


class FileInitialization(InitializationStructure):
    display_name = "Load from file"
    description = "Load initial points from a file"

    parameters = {
        "path": {
            "type": str,
            "default": "",
            "label": "File path",
            "description": "Use already sampled data"
        }
    }

    def generate(self, bounds, path: str):
        data = json.loads(Path(path).read_text())
        return torch.tensor(data["X"], dtype=torch.float)
