from typing import Sequence

try:
    from inputs.input_structure import InputStructure
except ModuleNotFoundError:
    # allow running the module directly (in __main__)
    from input_structure import InputStructure


class GasJetHeight(InputStructure):
    """Test"""
    
    def __init__(self, bounds: Sequence[float]=(0, 5)):
        "bounds defines the boundaries of the system"
        
        name = "gas_jet_height"
        unit = "um"
        self._safe_bounds = (0, 25)
        InputStructure.__init__(self, name, bounds, unit)
    
    @property
    def safe_bounds(self) -> Sequence[float]:
        return self._safe_bounds

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