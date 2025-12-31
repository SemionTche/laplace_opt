try:
    from model_construction.objectives.objective_structure import ObjectiveStructure
except ModuleNotFoundError:
    # allow running the module directly (in __main__)
    from objective_structure import ObjectiveStructure

class ElectronCharge(ObjectiveStructure):

    def __init__(self):
        name = "electron_charge"
        unit = "pC"
        minimize = False

        description = "The electron charge"
        symbol = r"$Q$"

        ObjectiveStructure.__init__(self, name, unit, minimize, description, symbol)


    def get_value(self) -> None:
        pass


if __name__ == "__main__":
    e = ElectronCharge(True)
    print(e)