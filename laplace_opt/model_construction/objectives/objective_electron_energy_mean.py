from laplace_opt.model_construction import ObjectiveStructure


class ElectronEnergyMean(ObjectiveStructure):
    '''
    Objective definition for the electron mean energy.

    This class defines the optimization direction (minimize or maximize),
    measurement source address, payload key, and metadata associated with
    the electron beam mean energy objective.
    '''

    def __init__(self, minimize: bool = False):
        '''
        Initialize the electron mean energy objective.

        Args:
            minimize: (bool)
                If True, the objective will be minimized.
                If False, the objective will be maximized.
        '''
        name = "electron_energy_mean"
        unit = "MeV"

        description = "The spectrum mean energy"
        symbol = r"$E_0$"

        ip = "147.250.140.65"
        port = "5556"
        position_index = 0

        output_key = "electron_energy_mean"

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
