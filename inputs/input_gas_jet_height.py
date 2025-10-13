from input_structure import InputStructure
from typing import Sequence

class GasJetHeight(InputStructure):

    def __init__(self, bounds: Sequence[float]=(0, 5)):
        name="gas_jet_height"
        InputStructure.__init__(self, name, bounds)
    
    def get_position(self) -> None:
        pass

if __name__ == "__main__":
    gas_jet_height = GasJetHeight(bounds=(0, 4))
    print(gas_jet_height)
    print("Position: ", gas_jet_height.get_position())

    gas_jet_height.set_bounds((1, 3))
    print(gas_jet_height)