from laplace_opt.model_construction.objectives.objective_structure import ObjectiveStructure


class ElectronEnergyMean(ObjectiveStructure):

    def __init__(self, minimize: bool = False):
        name = "electron_energy_mean"
        unit = "MeV"

        description = "The spectrum mean energy"
        symbol = r"$E_0$"

        # address = "tcp://147.250.140.65:5556"
        # address = "tcp://192.168.1.191:5556"
        position_index = 0
        # ip = "192.168.1.191"
        ip = "147.250.140.65"
        port = "5556"

        output_key = "electron_energy_mean"

        ObjectiveStructure.__init__(self, name, unit, minimize, description, symbol, ip, port, position_index, output_key)


    def get_value(self) -> None:
        pass