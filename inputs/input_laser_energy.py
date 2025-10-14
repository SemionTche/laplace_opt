from typing import Sequence

try:
    from inputs.input_structure import InputStructure
except ModuleNotFoundError:
    # allow running the module directly (in __main__)
    from input_structure import InputStructure

class LaserEnergy(InputStructure):

    def __init__(self, bounds: Sequence[float]=(0, 5)):
        name = "laser_energy"
        unit = "J"
        safe_bounds = (0, 100)
        InputStructure.__init__(self, name, bounds, safe_bounds, unit)

    def get_position(self) -> None:
        pass

    def set_position(self, position: float) -> None:
        pass

if __name__ == "__main__":
    laser_energy = LaserEnergy(bounds=(0, 4))
    print(laser_energy)
    print("Position: ", laser_energy.get_position())

    laser_energy.set_bounds((1, 3))
    print(laser_energy)