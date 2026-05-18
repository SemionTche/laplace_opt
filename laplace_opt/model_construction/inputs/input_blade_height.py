# libraries
from typing import Sequence

# project
from laplace_opt.model_construction import InputStructure


class BladeHeight(InputStructure):
    '''
    Input definition for the vertical position of the blade.

    This class specifies the optimization bounds, safe operating bounds,
    hardware address, and metadata associated with the blade height
    control parameter.
    '''
    
    def __init__(self, bounds: Sequence[float]=(150, 15000)):
        '''
        Initialize the blade height input.

        Args:
            bounds: (Sequence[float]) 
                Optimization bounds (min, max) in millimeters.
                These define the search space limits.
        '''
        name = "blade_height"
        unit = "um"
        safe_bounds = (100, 25000)

        ip = "10.0.5.1"
        port = "9633"
        
        description = "Vertical position of the blade."
        symbol = "y_blade"

        position_index = 10
        
        InputStructure.__init__(
            self, 
            name=name,
            bounds=bounds, 
            safe_bounds=safe_bounds,
            unit=unit,
            ip=ip,
            port=port,
            description=description,
            symbol=symbol,
            position_index=position_index
        )
