# libraries
from typing import Sequence

# project
from laplace_opt.model_construction import InputStructure


class GasJetLongitudinal(InputStructure):
    '''
    Input definition for the longitudinal position of the gas jet.

    This class defines the optimization bounds, safe operating bounds,
    hardware address, and metadata associated with the gas jet position
    along the propagation axis.
    '''

    def __init__(self, bounds: Sequence[float]=(0, 15)):
        '''
        Initialize the gas jet longitudinal input.

        Args:
            bounds: (Sequence[float])
                Optimization bounds (min, max) in millimeters.
                These define the search space limits.
        '''
        name = "gas_jet_longitudinal"
        unit = "mm"
        safe_bounds = (-2.0, 10.0)

        ip = "147.250.140.65"
        port = "5555"

        description = "Position of the gas jet along the propagation axis."
        symbol = "z_gas"

        position_index = 1
        
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
