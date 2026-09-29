# libraries
from datetime import datetime
from copy import deepcopy
from typing import Any
import pathlib
import json

from laplace_log import log
from botorch.models.model import Model
from botorch.acquisition import AcquisitionFunction
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
    - Periodically writing a checkpoint file in torch format (`.pt`)
    - Storing observations, model weights and metadata

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
                Example: save_period=5 -> save every 5 updates.

            is_saving (bool):
                Enables or disables saving entirely.
        '''
        self.is_saving = is_saving          # whether to save or not
        self.save_period = save_period      # the period at which the checkpoint should be saved
        self.counter = 0                    # the current step of the optimization
        now = datetime.now()
        self.start_day = now.date().isoformat()                        # the date at which the saver started
        self.start_time = now.time().isoformat(timespec="seconds")     # the time at which the saver started

        if not self.is_saving:  # if not saving
            return              # end the initialization

        if is_date_folder(save_folder):         # if the given path got a date folder
            date_folder = save_folder           # use it
        else:                                   # else
            date_folder = save_folder / self.start_day
            date_folder.mkdir(exist_ok=True)    # make one

        # if it does not exist, make the folder inside which to save the checkpoint
        self.model_folder = date_folder / "model_observations"
        if not self.model_folder.exists():
            self.model_folder.mkdir(exist_ok=True)

        # get the optimization index
        idx = get_next_optimization_index(
            file_name_="model_observations_", 
            folder=self.model_folder, 
            ext="pt"
        )
        self.base_index = idx

        # store the model and acquisition hyperparameters
        self.model_state_history: dict[int, dict[str, Any]] = {}
        self.acq_state_history: dict[int, dict[str, Any]] = {}


    def save(self, 
             context: OptimizationContext, 
             opt_form: dict, 
             suggestion_history: list, 
             model: Model,
             acq_func: AcquisitionFunction,
             best_results: list[dict[str, int | str | bool | float | list[float]]],
             is_stop: bool=False) -> None:
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

            model (Model):
                Trained model instance.
            
            acq_func (AcquisitionFunction):
                The acquisition function of the optimization.
            
            best_results (list[dict]):
                List of best point for each objective, with some
                additional data.
            
            is_stop (bool):
                is the current call made by the 'stop action' of the interface.
        '''
        if not self.is_saving:
            return

        if not is_stop:         # do not increment the step
            self.counter += 1   # if the call comes from the user

        if self.counter % self.save_period != 0 and not is_stop:   # if it's not the period and not a manual save
            return                                                 # don't save

        now = datetime.now()

        # register the state
        model_state = model.state_dict()
        acq_state = acq_func.state_dict()
        self.model_state_history[self.counter + 1] = deepcopy(model_state)
        self.acq_state_history[self.counter + 1] = deepcopy(acq_state)

        # make the checkpoit to save
        checkpoint = {

            # saving metadata
            "metadata": {
                "saving_date": now.date().isoformat(),
                "saving_time": now.time().isoformat(timespec="seconds"),
                "start_day": self.start_day,
                "start_time": self.start_time,
                "n_observations": len(context._observations),
                "n_inputs": context.n_inputs,
                "n_obj": context.n_obj,
                "n_init": context.n_init,
                "optimization_step": self.counter,
                "init_and_opt_step": self.counter + 1,
                "tensor_info": {
                    "dtype": str(context.X_physical.dtype),
                    "device": str(context.X_physical.device),
                },
                "criterium": opt_form["criterium"]
            },
            
            # problem parameters
            "problem": {
                "bounds": context.bounds,
                "inputs": context.get_input_state_dict(),
                "objectives": context.get_obj_state_dict(),
                "init": {
                    "class": (
                        opt_form["init"]["cls"].__module__
                        + "."
                        + opt_form["init"]["cls"].__qualname__
                    ),
                    "params": opt_form["init"]["params"],
                },
                "strategy": {
                    "class": (
                        opt_form["opt"]["pipeline"]["strategy"]["cls"].__module__
                        + "."
                        + opt_form["opt"]["pipeline"]["strategy"]["cls"].__qualname__
                    ),
                    "params": opt_form["opt"]["pipeline"]["strategy"]["params"],
                },
                "acquisition": {
                    "class": (
                        opt_form["opt"]["pipeline"]["acquisition"]["cls"].__module__
                        + "."
                        + opt_form["opt"]["pipeline"]["acquisition"]["cls"].__qualname__
                    ),
                    "params": opt_form["opt"]["pipeline"]["acquisition"]["params"],                    
                },
                "opt_form": json.dumps(opt_form, cls=OptimizationJSONEncoder),
            },
            
            # data
            "observations": {
                "X_physical": context.X_physical,
                "X_normalized": context.X_normalized,
                "Y_opt_space": context.Y_opt_space,
                "Y_physical": context.Y_physical,
                "shot_numbers": context.shot_number_list
            },

            "model":{
                "model_class": (
                    model.__class__.__module__ 
                    + "." 
                    + model.__class__.__qualname__
                ),
                "model_state_dict": model_state,
                "model_state_history": self.model_state_history
            },
            
            "acquisition": {
                "acquisition_class": (
                    acq_func.__class__.__module__ + 
                    "." + 
                    acq_func.__class__.__qualname__
                ),
                "acquisition_state_dict": acq_state,
                "acq_state_history": self.acq_state_history
            },

            "best_results": best_results,

            "suggestions": suggestion_history,
            
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

            log.info(f"model_observations_{self.base_index:06d} file saved. (step={self.counter})")
        
        except Exception as e:
            log.error(f"Error: could not save the model_observations_{self.base_index:06d},\n"
                      f"(step={self.counter}),\n"
                      f"because: {e}")
