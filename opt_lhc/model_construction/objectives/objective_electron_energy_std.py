try:
    from model_construction.objectives.objective_structure import ObjectiveStructure
except ModuleNotFoundError:
    # allow running the module directly (in __main__)
    from objective_structure import ObjectiveStructure

class ElectronEnergyStd(ObjectiveStructure):

    def __init__(self):
        name = r"$\sigma_E$"
        unit = "MeV"
        minimize = True
        ObjectiveStructure.__init__(self, name, unit, minimize)


    def get_value(self) -> None:
        pass


if __name__ == "__main__":
    e = ElectronEnergyStd(True)
    print(e)