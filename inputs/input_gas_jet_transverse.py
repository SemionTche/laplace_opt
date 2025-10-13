from input_structure import InputStructure
from typing import Sequence

class GasJetTransverse(InputStructure):

    def __init__(self, bounds: Sequence[float]=(0, 5)):
        name = "gas_jet_transverse"
        unit = "um"
        InputStructure.__init__(self, name, bounds, unit)
    
    def get_position(self) -> None:
        pass

if __name__ == "__main__":
    gas_jet_transverse = GasJetTransverse(bounds=(0, 4))
    print(gas_jet_transverse)
    print("Position: ", gas_jet_transverse.get_position())

    gas_jet_transverse.set_bounds((1, 3))
    print(gas_jet_transverse)