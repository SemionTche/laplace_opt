try:
    from model_construction.objectives.objective_structure import ObjectiveStructure
except ModuleNotFoundError:
    # allow running the module directly (in __main__)
    from objective_structure import ObjectiveStructure

class ElectronEnergyMean(ObjectiveStructure):

    def __init__(self, minimize: bool):
        name = r"$E_0$"
        unit = "MeV"
        ObjectiveStructure.__init__(self, name, minimize, unit)


    def get_value(self) -> None:
        pass


if __name__ == "__main__":
    e = ElectronEnergyMean(True)
    print(e)