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
        
        ObjectiveStructure.__init__(self, name, unit, minimize, description, symbol)


    def get_value(self) -> None:
        pass


if __name__ == "__main__":
    e = ElectronEnergyStd(True)
    print(e)