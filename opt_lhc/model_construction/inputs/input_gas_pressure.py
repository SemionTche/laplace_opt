from typing import Sequence

try:
    from model_construction.inputs.input_structure import InputStructure
except ModuleNotFoundError:
    # allow running the module directly (in __main__)
    from input_structure import InputStructure

class GasPressure(InputStructure):

    def __init__(self, gas_type: str = "N2", bounds: Sequence[float]=(0, 5)):
        
        name = "gas_pressure"
        unit = "bar"
        self._gas_type = gas_type
        safe_bounds = (0.0, 300.0)
        address = "tmp 4"

        description = "Gas pressure"
        symbol = "P_gas"

        position_index = 0
        
        InputStructure.__init__(
            self, 
            name=name, 
            bounds=bounds, 
            safe_bounds=safe_bounds, 
            unit=unit, 
            address=address, 
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
    

if __name__ == "__main__":
    gas_presure = GasPressure(bounds=(0, 4))
    print(gas_presure)
    print("Position: ", gas_presure.get_position())
    
    gas_presure.set_bounds((1, 3))
    print(gas_presure)