from typing import Sequence

try:
    from inputs.input_structure import InputStructure
except ModuleNotFoundError:
    # allow running the module directly (in __main__)
    from input_structure import InputStructure

class GasJetTransverse(InputStructure):

    def __init__(self, bounds: Sequence[float]=(0, 5)):
        name = "gas_jet_transverse"
        unit = "um"
        safe_bounds = (0, 25)
        InputStructure.__init__(self, name, bounds, safe_bounds, unit)

    def get_position(self) -> None:
        pass

    def set_position(self, position: float) -> None:
        pass

if __name__ == "__main__":
    gas_jet_transverse = GasJetTransverse(bounds=(0, 4))
    print(gas_jet_transverse)
    print("Position: ", gas_jet_transverse.get_position())

    gas_jet_transverse.set_bounds((1, 3))
    print(gas_jet_transverse)
    print(gas_jet_transverse.__class__.__name__)
    print(gas_jet_transverse.name)
    print(gas_jet_transverse.safe_bounds)