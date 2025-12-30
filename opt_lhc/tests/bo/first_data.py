import h5py
import numpy as np
import time

with h5py.File("save/model.hdf5", "w") as f:
    f.create_dataset("next_candidates", data=np.array([[1.0, 2.0]]))
    f.create_dataset("step", data=1)
    f.create_dataset("timestamp", data=time.time())
