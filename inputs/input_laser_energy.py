from input_structure import InputStructure
from typing import Sequence

class LaserEnergy(InputStructure):

    def __init__(self, bounds: Sequence[float]=(0, 5)):
        name = "laser_energy"
        unit = "J"
        InputStructure.__init__(self, name, bounds, unit)
    
    def get_position(self) -> None:
        pass

if __name__ == "__main__":
    laser_energy = LaserEnergy(bounds=(0, 4))
    print(laser_energy)
    print("Position: ", laser_energy.get_position())

    laser_energy.set_bounds((1, 3))
    print(laser_energy)