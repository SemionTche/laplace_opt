# libraries
from abc import ABC, abstractmethod

from botorch.acquisition import AcquisitionFunction
from botorch.models.model import Model

# project
from laplace_opt.core.optimizerContext import OptimizationContext


class AcquisitionStructure(ABC):
    '''
    Base class for acquisition function structures.

    This class defines a common interface for building acquisition functions
    used in Bayesian optimization. Subclasses should implement the `build_acq`
    method to return a configured acquisition function.
    '''
    
    display_name: str = "Acquisition Structure"
    description: str = "Acquisition Structure description"
    
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


    @abstractmethod
    def build_acq(self,
                  model: Model, 
                  context: OptimizationContext, 
                  **params) -> AcquisitionFunction:
        '''
        Construct the acquisition function.

        Args:
            model:
                Fitted surrogate model representing the posterior.
            
            context: (OptimizationContext)
                context providing access to baseline data
                and other relevant information.
            
            **params:
                Additional keyword arguments.

        Returns:
            Configured acquisition function ready for optimization.
        '''
        pass
