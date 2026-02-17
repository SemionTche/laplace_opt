# libraries
from datetime import date
import time
import pathlib
import json

from laplace_log import log
from torch.nn import Module
import torch

# project
from .optimizerContext import OptimizationContext
from ..utils.model_form import is_date_folder
from ..utils.save_form import get_next_optimization_index
from ..utils.json_encoder import OptimizationJSONEncoder


class ModelSaver:
    '''
    Handles periodic saving of the optimization state.

    This class is responsible for:
    - Creating the appropriate saving directory structure
    - Periodically writing a checkpoint file in torch format (.pt)
    - Storing observations, model weights, metadata, and RNG state

    The saved checkpoint allows full optimization resumption.
    '''

    def __init__(self, 
                 save_folder: pathlib.Path, 
                 save_period: int, 
                 is_saving: bool):
        '''
        Initialize the ModelSaver.

        Args:
            save_folder (Path):
                Base folder where optimization data should be saved.
                If not already a date folder, a new one is created.

            save_period (int):
                Save frequency (in optimization steps).
                Example: save_period=5 → save every 5 updates.

            is_saving (bool):
                Enables or disables saving entirely.
        '''
        self.is_saving = is_saving          # whether to save or not
        self.save_period = save_period      # the period at which the checkpoint should be saved
        self.counter = 0                    # the current step of the optimization
        self.start_time = time.time()       # the time at which the saver started

        if not self.is_saving:  # if not saving
            return              # end the initialization

        if is_date_folder(save_folder):         # if the given path got a date folder
            date_folder = save_folder           # use it
        else:                                   # else
            date_folder = save_folder / date.today().isoformat()
            date_folder.mkdir(exist_ok=True)    # make one

        # if it does not exist, make the folder inside which to save the checkpoint
        self.model_folder = date_folder / "model_observations"
        if not self.model_folder.exists():
            self.model_folder.mkdir(exist_ok=True)

        # get the optimization index
        idx = get_next_optimization_index(
            "model_observations_", self.model_folder, "pt"
        )
        self.base_index = idx


    def save(self, 
             context: OptimizationContext, 
             opt_form: dict, 
             suggestion_history: list, 
             model: Module) -> None:
        '''
        Save a checkpoint of the current optimization state.

        This method:
        - Increments the internal step counter
        - Saves only if the save_period condition is met
          along with the is_saving internal attribute
        - Serializes observations, model state, and metadata
        - Writes safely using a temporary file before replacement

        Args:
            context (OptimizationContext):
                Contains all observed X and Y data.

            opt_form (dict):
                Full optimization configuration dictionary.

            suggestion_history (list):
                Previously suggested candidate tensors.

            model:
                Trained model instance (must implement state_dict()).
        '''
        if not self.is_saving:
            return

        self.counter += 1

        if self.counter % self.save_period != 0:
            return

        # make the checkpoit to save
        checkpoint = {
            "metadata": {
                "saving_date": date.today().isoformat(),
                "start_time": self.start_time,
                "saving_time": time.time(),
                "n_observations": len(context._observations),
                "optimization_step": self.counter
            },
            "problem": {
                "bounds": context.bounds,
                "opt_form": json.dumps(opt_form, cls=OptimizationJSONEncoder),
            },
            "observations": {
                "X_physical": context.X_physical,
                "X_normalized": context.X_normalized,
                "Y_opt_space": context.Y_opt_space,
                "Y_physical": context.Y_physical,
            },
            "suggestions": suggestion_history,
            "model_state_dict": model.state_dict(),
            "rng_state": torch.get_rng_state()
        }

        # make the file name
        filename = self.model_folder / f"model_observations_{self.base_index:06d}.pt"
        
        try:
            log.info("Saving model_observations file...")
            
            # write using a tmp file to prevent failing
            tmp_filename = filename.with_suffix(".tmp")    # change the suffix for 'tmp'
            torch.save(checkpoint, tmp_filename)           # save the file
            tmp_filename.replace(filename)                 # use the 'pt' extension

            log.info(f"model_observations_{self.base_index:06d} file saved.")
        
        except Exception as e:
            log.error(f"Error: could not save the model_observations_{self.base_index:06d} because: {e}")
