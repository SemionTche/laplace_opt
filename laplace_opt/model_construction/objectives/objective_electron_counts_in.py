# project
from laplace_opt.model_construction import ObjectiveStructure


class ElectronCountsIn(ObjectiveStructure):
    '''
    Objective definition for the electron counts in.

    This class defines the optimization direction (minimize or maximize),
    measurement source address, payload key, and metadata associated with
    the electron counts in objective.
    '''

    def __init__(self, minimize = False):
        '''
        Initialize the electron counts in objective.

        Args:
            minimize: (bool)
                If True, the objective will be minimized.
                If False, the objective will be maximized.
        '''
        name = "electron_count_in"
        unit = "pC"

        description = "The electron counts in"
        symbol = r"$Q_{In}$"

        ip = "10.0.33.3"
        port = "1423"
        position_index = 0

        output_key = "counts_in"

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
