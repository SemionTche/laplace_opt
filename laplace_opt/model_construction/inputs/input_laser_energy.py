# libraries
from typing import Sequence

# project
from laplace_opt.model_construction.inputs.input_structure import InputStructure

class LaserEnergy(InputStructure):

    def __init__(self, bounds: Sequence[float]=(0, 5)):
        
        name = "laser_energy"
        unit = "J"
        safe_bounds = (0.0, 100.0)
        # address = "tmp 5"
        ip = "tmp"
        port = "5"

        description = "Laser energy"
        symbol = "E_laser"

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

    def get_position(self) -> None:
        pass

    def set_position(self, position: float) -> None:
        pass