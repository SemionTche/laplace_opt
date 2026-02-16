from typing import Sequence

from laplace_opt.model_construction.inputs.input_structure import InputStructure

class GasPressure(InputStructure):

    def __init__(self, gas_type: str = "N2", bounds: Sequence[float]=(0, 5)):
        
        name = "gas_pressure"
        unit = "bar"
        self._gas_type = gas_type
        safe_bounds = (0.0, 300.0)
        # address = "tmp 4"

        ip = "tmp"
        port = "4"

        description = "Gas pressure"
        symbol = "P_gas"

        position_index = 0
        
        InputStructure.__init__(
            self, 
            name=name, 
            bounds=bounds, 
            safe_bounds=safe_bounds, 
            unit=unit, 
            # address=address, 
            ip=ip,
            port=port,
            description=description,
            symbol=symbol,
            position_index=position_index
        )
    
    @property
    def gas_type(self) -> str:
        return self._gas_type

    def get_position(self) -> None:
        pass
    
    def set_position(self, position: float) -> None:
        pass
