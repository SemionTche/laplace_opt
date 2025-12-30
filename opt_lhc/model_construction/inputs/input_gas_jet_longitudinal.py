from typing import Sequence

try:
    from model_construction.inputs.input_structure import InputStructure
except ModuleNotFoundError:
    # allow running the module directly (in __main__)
    from input_structure import InputStructure

class GasJetLongitudinal(InputStructure):

    def __init__(self, bounds: Sequence[float]=(0, 5)):
        name = "gas_jet_longitudinal"
        safe_bounds = (0, 25)
        unit = "um"
        address = "tmp 2"
        InputStructure.__init__(self, name, bounds, safe_bounds, unit, address)

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