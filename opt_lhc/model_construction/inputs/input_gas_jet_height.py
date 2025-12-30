from typing import Sequence

try:
    from model_construction.inputs.input_structure import InputStructure
except ModuleNotFoundError:
    # allow running the module directly (in __main__)
    from input_structure import InputStructure


class GasJetHeight(InputStructure):
    
    def __init__(self, bounds: Sequence[float]=(0, 15)):
        "bounds defines the boundaries of the system"
        
        name = "gas_jet_height"
        unit = "mm"
        safe_bounds = (0, 15)
        address = "tmp 1"
        InputStructure.__init__(self, name, bounds, safe_bounds, unit, address)

    def get_position(self) -> None:
        pass

    def set_position(self, position: float) -> None:
        pass

if __name__ == "__main__":
    gas_jet_height = GasJetHeight(bounds=(0, 4))
    print(gas_jet_height)
    print("Position: ", gas_jet_height.get_position())

    gas_jet_height.set_bounds((1, 3))
    print(gas_jet_height)