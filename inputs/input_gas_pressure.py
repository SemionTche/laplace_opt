from input_structure import InputStructure
from typing import Sequence

class GasPressure(InputStructure):

    def __init__(self, gas_type: str="N2", bounds: Sequence[float]=(0, 5)):
        name="gas_pressure"
        self._gas_type = gas_type
        InputStructure.__init__(self, name, bounds)
    
    @property
    def type(self) -> str:
        return self._gas_type

    def get_position(self) -> None:
        pass
    

if __name__ == "__main__":
    gas_presure = GasPressure(bounds=(0, 4))
    print(gas_presure)
    print("Position: ", gas_presure.get_position())
    
    gas_presure.set_bounds((1, 3))
    print(gas_presure)