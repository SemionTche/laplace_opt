# project
from laplace_opt.model_construction import ObjectiveStructure


class ElectronEnergyStd(ObjectiveStructure):
    '''
    Objective definition for the electron energy standard deviation.

    This class defines the optimization direction (minimize or maximize),
    measurement source address, payload key, and metadata associated with
    the electron energy spread objective.
    '''

    def __init__(self, minimize: bool=True):
        '''
        Initialize the electron energy standard deviation objective.

        Args:
            minimize: (bool)
                If True, the objective will be minimized.
                If False, the objective will be maximized.
        '''
        
        name = "electron_energy_std"
        unit = "MeV"
        
        description = "The spectrum energy standard deviation"
        symbol = r"$\sigma_E$"

        ip = "147.250.140.65"
        port = "5556"
        position_index = 0

        output_key = "electron_energy_std"
        
        ObjectiveStructure.__init__(
            self, 
            name=name, 
            unit=unit, 
            minimize=minimize, 
            description=description, 
            symbol=symbol, 
            ip=ip, 
            port=port, 
            position_index=position_index, 
            output_key=output_key
        )
