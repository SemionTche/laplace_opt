# libraries
from abc import ABC, abstractmethod


class InitializationStructure(ABC):
    """
    Base class for all initialization strategies.
    """

    display_name: str = "Initialization Structure"
    description: str = ""
    
    parameters: dict[str, dict] = {
        "example_int": {
            "type": int,
            "min": 1,
            "max": 2,
            "default": 1,
            "label": "example of int parameter",
            "description": "tooltip for this parameter"
        },
        "example_float": {
            "type": float,
            "decimals": 3,
            "step": 0.1,
            "min": -1e-9,
            "max": 1e9,
            "default": 0,
            "label": "example of float parameter",
            "description": "tooltip for this parameter"
        },
        "example_bool": {
            "type": bool,
            "default": True,
            "label": "Shuffle samples",
            "label": "example of bool parameter",
            "description": "tooltip for this parameter"
        }
    }

    @classmethod
    def get_parameters(cls) -> dict[str, dict]:
        return cls.parameters

    @abstractmethod
    def generate(self, bounds, **kwargs):
        '''
        Returns initial sample coordinates (X vector).
        '''
        pass
