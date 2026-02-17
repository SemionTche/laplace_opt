# libraries
from pathlib import Path

from laplace_log import log
import torch

# project
from laplace_opt.model_construction import InitializationStructure


class FileInitialization(InitializationStructure):
    '''
    Initialization strategy based on loading previously sampled data from a file.

    This class restores initial design points and corresponding observations
    from a saved checkpoint file. It allows the optimization process to
    resume from existing data instead of generating new initial samples.
    '''
    display_name = "Load from file"
    description = "Load initial points from a 'model_observations_*.pt' file"

    parameters = {
        "path": {
            "type": str,
            "mode": "file",
            "default": "",
            "label": "File path",
            "description": "Use already sampled data"
        }
    }

    def generate(self, 
                 bounds: torch.Tensor, 
                 path: str) -> tuple[torch.Tensor, torch.Tensor]:
        '''
        Load initial samples and observations from a checkpoint file.

        Args:
            bounds: (torch.Tensor)
                Tensor of shape [2, d] defining lower and upper bounds
                of the search space. This argument is required by the
                interface but is not used when loading from file.
            
            path: (str)
                Path to a checkpoint file containing stored observations.
                The file must contain "observations" with keys
                "X_physical" and "Y_physical".

        Returns:
            tuple[torch.Tensor, torch.Tensor]:
                A tuple (X, Y) where:
                    - X is a tensor of input points in physical space.
                    - Y is a tensor of corresponding objective values in physical space.
                Both tensors are returned in double precision.

        Raises:
            ValueError:
                If the file does not contain the required keys or
                cannot be properly loaded.
        '''
        checkpoint = torch.load(Path(path))
        
        try:
            X: torch.Tensor = checkpoint["observations"]["X_physical"]
            Y: torch.Tensor = checkpoint["observations"]["Y_physical"]
            return X.double(), Y.double()
        
        except Exception as e:
            error_msg = f"Error: {e}\nCould not read X or Y from the given file."
            log.error(error_msg)
            raise ValueError(error_msg)
