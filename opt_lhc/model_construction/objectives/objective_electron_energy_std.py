try:
    from model_construction.objectives.objective_structure import ObjectiveStructure
except ModuleNotFoundError:
    # allow running the module directly (in __main__)
    from objective_structure import ObjectiveStructure

class ElectronEnergyStd(ObjectiveStructure):

    def __init__(self):
        
        name = "electron_energy_std"
        unit = "MeV"
        minimize = True
        
        description = "The spectrum energy standard deviation"
        symbol = r"$\sigma_E$"

        address = "tcp://147.250.140.65:5556"
        position_index = 2

        output_key = "electron_energy_std"
        
        ObjectiveStructure.__init__(self, name, unit, minimize, description, symbol, address, position_index, output_key)


    def get_value(self) -> None:
        pass