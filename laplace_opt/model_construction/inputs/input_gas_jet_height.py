# libraries
from typing import Sequence

# project
from laplace_opt.model_construction import InputStructure


class GasJetHeight(InputStructure):
    '''
    Input definition for the vertical position of the gas jet.

    This class specifies the optimization bounds, safe operating bounds,
    hardware address, and metadata associated with the gas jet height
    control parameter.
    '''
    
    def __init__(self, bounds: Sequence[float]=(0, 15)):
        '''
        Initialize the gas jet height input.

        Args:
            bounds: (Sequence[float]) 
                Optimization bounds (min, max) in millimeters.
                These define the search space limits.
        '''
        name = "gas_jet_height"
        unit = "mm"
        safe_bounds = (-2.0, 10.0)

        ip = "147.250.140.65"
        port = "5555"
        
        description = "Vertical position of the gas jet."
        symbol = "y_gas"

        position_index = 0
        
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
