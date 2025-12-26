from abc import ABC, abstractmethod
from typing import Dict, Any

class InitializationStructure(ABC):
    """
    Base class for all initialization strategies.
    """

    # --- metadata for GUI ---
    display_name: str = "Base Initialization"
    description: str = ""
    parameters: Dict[str, dict] = {}
    # parameters example:
    # {
    #   "n_samples": {"type": int, "default": 16, "min": 1, "max": 1024}
    # }

    @classmethod
    def get_parameters(cls) -> Dict[str, dict]:
        return cls.parameters

    @abstractmethod
    def generate(self, bounds, **kwargs):
        """
        Returns initial samples (X, Y or just X depending on design).
        """
        pass
