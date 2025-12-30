try:
    from model_construction.objectives.objective_structure import ObjectiveStructure
except ModuleNotFoundError:
    # allow running the module directly (in __main__)
    from objective_structure import ObjectiveStructure

class ElectronCharge(ObjectiveStructure):

    def __init__(self):
        name = r"$Q$"
        unit = "pC"
        default_minimize = False
        ObjectiveStructure.__init__(self, name, unit, default_minimize)


    def get_value(self) -> None:
        pass


if __name__ == "__main__":
    e = ElectronCharge(True)
    print(e)