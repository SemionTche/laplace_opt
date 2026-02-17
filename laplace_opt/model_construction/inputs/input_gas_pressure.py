# libraries
from typing import Sequence

# project
from laplace_opt.model_construction import InputStructure


class GasPressure(InputStructure):
    '''
    Input definition for the gas pressure parameter.

    This class specifies the optimization bounds, safe operating bounds,
    gas type, hardware address, and metadata associated with the gas
    pressure control variable.
    '''

    def __init__(self, gas_type: str = "N2", bounds: Sequence[float]=(0, 5)):
        
        name = "gas_pressure"
        unit = "bar"
        safe_bounds = (0.0, 100.0)

        ip = "tmp"
        port = "4"

        description = "Gas pressure"
        symbol = "P_gas"

        position_index = 0

        self.gas_type = gas_type
        
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
