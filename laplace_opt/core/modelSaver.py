from datetime import date
import time
import pathlib
import os
import json

from laplace_log import log

import torch

from .optimizerContext import OptimizationContext
from ..utils.model_form import is_date_folder
from ..utils.save_form import get_next_optimization_index
from ..utils.json_encoder import OptimizationJSONEncoder

class ModelSaver:

    def __init__(self, save_folder: pathlib.Path, save_period: int, is_saving: bool):
        self.is_saving = is_saving
        self.save_period = save_period
        self.counter = 0
        self.start_time = time.time()

        if not self.is_saving:
            return

        if is_date_folder(save_folder):
            date_folder = save_folder
        else:
            date_folder = save_folder / date.today().isoformat()
            date_folder.mkdir(exist_ok=True)

        self.model_folder = date_folder / "model_observations"
        self.model_folder.mkdir(exist_ok=True)

        idx = get_next_optimization_index(
            "model_observations_", self.model_folder, "pt"
        )
        self.base_index = idx


    def save(self, context: OptimizationContext, opt_form, suggestion_history, model):
        if not self.is_saving:
            return

        self.counter += 1

        if self.counter % self.save_period != 0:
            return

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

        filename = self.model_folder / f"model_observations_{self.base_index:06d}.pt"
        
        try:
            log.info("Saving model_observations file...")
            tmp_filename = filename.with_suffix(".tmp")

            torch.save(checkpoint, tmp_filename)
            tmp_filename.replace(filename)
            log.info("model_observations file saved.")
        except Exception as e:
            log.error(f"Error: {e}")
