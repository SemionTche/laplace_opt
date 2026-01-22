from typing import Sequence

try:
    from model_construction.inputs.input_structure import InputStructure
except ModuleNotFoundError:
    # allow running the module directly (in __main__)
    from input_structure import InputStructure

class GasJetLongitudinal(InputStructure):

    def __init__(self, bounds: Sequence[float]=(0, 15)):
        
        name = "gas_jet_longitudinal"
        unit = "mm"
        safe_bounds = (-2.0, 10.0)
        # address = "147.250.140.65:5555"
        # address = "192.168.1.191:5555"
        # ip = "192.168.1.191"
        ip = "147.250.140.65"
        port = "5555"

        description = "Position of the gas jet along the propagation axis."
        symbol = "z_gas"

        position_index=1
        
        InputStructure.__init__(
            self, 
            name=name, 
            bounds=bounds, 
            safe_bounds=safe_bounds, 
            unit=unit, 
            # address=address, 
            ip = ip,
            port = port,
            description=description,
            symbol=symbol,
            position_index=position_index
        )

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