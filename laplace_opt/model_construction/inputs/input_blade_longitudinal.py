# libraries
from typing import Sequence

# project
from laplace_opt.model_construction import InputStructure


class BladeLongitudinal(InputStructure):
    '''
    Input definition for the longitudinal position of the blade.

    This class defines the optimization bounds, safe operating bounds,
    hardware address, and metadata associated with the blade position
    along the propagation axis.
    '''

    def __init__(self, bounds: Sequence[float]=(150, 15000)):
        '''
        Initialize the blade longitudinal input.

        Args:
            bounds: (Sequence[float])
                Optimization bounds (min, max) in millimeters.
                These define the search space limits.
        '''
        name = "blade_longitudinal"
        unit = "um"
        safe_bounds = (100, 25000)

        ip = "10.0.5.1"
        port = "9633"

        description = "Position of the blade along the propagation axis."
        symbol = "z_blade"

        position_index = 13
        
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
