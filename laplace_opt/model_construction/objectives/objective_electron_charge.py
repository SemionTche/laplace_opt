# project
from laplace_opt.model_construction import ObjectiveStructure


class ElectronCharge(ObjectiveStructure):
    '''
    Objective definition for the electron beam charge.

    This class defines the optimization direction (minimize or maximize),
    measurement source address, payload key, and metadata associated with
    the electron beam charge objective.
    '''

    def __init__(self, minimize = False):
        '''
        Initialize the electron charge objective.

        Args:
            minimize: (bool)
                If True, the objective will be minimized.
                If False, the objective will be maximized.
        '''
        name = "electron_charge"
        unit = "pC"

        description = "The electron charge"
        symbol = r"$Q$"

        ip = "147.250.140.65"
        port = "5556"
        position_index = 0

        output_key = "electron_charge"

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
