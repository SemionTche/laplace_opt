from typing import Sequence

try:
    from inputs.input_structure import InputStructure
except ModuleNotFoundError:
    # allow running the module directly (in __main__)
    from input_structure import InputStructure

class GasPressure(InputStructure):

    def __init__(self, gas_type: str="N2", bounds: Sequence[float]=(0, 5)):
        name = "gas_pressure"
        unit = "bar"
        self._gas_type = gas_type
        self._safe_bounds = (0, 300)
        InputStructure.__init__(self, name, bounds, unit)
    
    @property
    def gas_type(self) -> str:
        return self._gas_type

    @property
    def safe_bounds(self) -> Sequence[float]:
        return self._safe_bounds

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