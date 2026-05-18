# project
from laplace_opt.model_construction import ObjectiveStructure


class ElectronCountsOut(ObjectiveStructure):
    '''
    Objective definition for the electron counts out.

    This class defines the optimization direction (minimize or maximize),
    measurement source address, payload key, and metadata associated with
    the electron counts out objective.
    '''

    def __init__(self, minimize = True):
        '''
        Initialize the electron counts in objective.

        Args:
            minimize: (bool)
                If True, the objective will be minimized.
                If False, the objective will be maximized.
        '''
        name = "electron_count_out"
        unit = "pC"

        description = "The electron counts out"
        symbol = r"$Q_{Out}$"

        ip = "10.0.33.3"
        port = "1423"
        position_index = 0

        output_key = "counts_out"

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
