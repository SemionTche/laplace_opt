# core/modelSaver.py
import time
import h5py
import torch
import pathlib


class ModelSaver:
    def __init__(self, folder: pathlib.Path):
        self.file = folder / "model.hdf5"

    def save(
        self,
        train_X: torch.Tensor,
        train_Y: torch.Tensor,
        next_candidates: torch.Tensor,
        step: int,
        model_config: dict,
    ):
        with h5py.File(self.file, "w") as f:
            f.create_dataset("train_X", data=train_X.cpu().numpy())
            f.create_dataset("train_Y", data=train_Y.cpu().numpy())
            f.create_dataset("next_candidates", data=next_candidates.cpu().numpy())
            f.create_dataset("step", data=step)
            f.create_dataset("timestamp", data=time.time())

            for k, v in model_config.items():
                f.attrs[k] = str(v)
