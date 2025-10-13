from input_structure import InputStructure
from typing import Sequence

class GasJetLongitudinal(InputStructure):

    def __init__(self, bounds: Sequence[float]=(0, 5)):
        name = "gas_jet_longitudinal"
        unit = "um"
        InputStructure.__init__(self, name, bounds, unit)
    
    def get_position(self) -> None:
        pass

    def set_position(self, position: float) -> None:
        pass

if __name__ == "__main__":
    gas_jet_longitudinal = GasJetLongitudinal(bounds=(0, 4))
    print(gas_jet_longitudinal)
    print("Position: ", gas_jet_longitudinal.get_position())

    gas_jet_longitudinal.set_bounds((1, 3))
    print(gas_jet_longitudinal)