from laplace_opt.model_construction.objectives.objective_structure import ObjectiveStructure


class ElectronCharge(ObjectiveStructure):

    def __init__(self):
        name = "electron_charge"
        unit = "pC"
        minimize = False

        description = "The electron charge"
        symbol = r"$Q$"

        # address = "tcp://147.250.140.65:5556"
        # address = "tcp://192.168.1.191:5556"
        # ip = "192.168.1.191"
        ip = "147.250.140.65"
        port = "5556"

        position_index = 0

        output_key = "electron_charge"

        ObjectiveStructure.__init__(self, name, unit, minimize, description, symbol, ip, port, position_index, output_key)


    def get_value(self) -> None:
        pass