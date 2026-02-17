# libraries
from abc import ABC, abstractmethod
from typing import Sequence

import torch


class InitializationStructure(ABC):
    '''
    Base class for all initializations.
    '''
    display_name: str = "Initialization Structure"
    description: str = "Structure description"
    
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
            "label": "example of bool parameter",
            "description": "tooltip for this parameter"
        }
    }


    @classmethod
    def get_parameters(cls) -> dict[str, dict]:
        '''Return the dictionary parameters of the initialization.'''
        return cls.parameters


    @abstractmethod
    def generate(self, bounds: Sequence[float], **kwargs) -> tuple[torch.Tensor, torch.Tensor | None]:
        '''
        Returns initial sample coordinates 
        (X vector, Y vector) in physical space.

        If the generation is only a sampling
        suggestion, it returns (X_physical, None)
        '''
        pass
