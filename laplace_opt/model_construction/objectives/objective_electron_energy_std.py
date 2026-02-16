from laplace_opt.model_construction.objectives.objective_structure import ObjectiveStructure


class ElectronEnergyStd(ObjectiveStructure):

    def __init__(self, minimize: bool=True):
        
        name = "electron_energy_std"
        unit = "MeV"
        
        description = "The spectrum energy standard deviation"
        symbol = r"$\sigma_E$"

        # address = "tcp://147.250.140.65:5556"
        # ip = "192.168.1.191"
        ip = "147.250.140.65"
        port = "5556"
        position_index = 0

        output_key = "electron_energy_std"
        
        ObjectiveStructure.__init__(self, name, unit, minimize, description, symbol, ip, port, position_index, output_key)


    def get_value(self) -> None:
        pass