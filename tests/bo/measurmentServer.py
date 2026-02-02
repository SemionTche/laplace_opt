import pathlib
import time
import h5py
import numpy as np

from PyQt6.QtWidgets import QApplication

from target_function_1 import target_function_1
from target_function_2 import target_function_2

from server_lhc.serverLHC import ServerLHC

from modelWatcher import ModelWatcher   # ✅ NEW


# ============================================================
# Storage
# ============================================================

SAVE_DIR = pathlib.Path("save")
SAVE_DIR.mkdir(exist_ok=True)

H5_FILE = SAVE_DIR / "measurements.hdf5"


def save_measurement(position, values):
    # --- Normalize inputs ---
    position = np.asarray(position, dtype=float).reshape(-1)
    values = np.asarray(values, dtype=float).reshape(-1)
    ts = np.array([time.time()])

    with h5py.File(H5_FILE, "a") as f:
        if "positions" not in f:
            f.create_dataset(
                "positions",
                data=position[None, :],          # (1, D)
                maxshape=(None, position.size),  # (N, D)
            )
            f.create_dataset(
                "values",
                data=values[None, :],            # (1, M)
                maxshape=(None, values.size),    # (N, M)
            )
            f.create_dataset(
                "timestamp",
                data=ts,                         # (1,)
                maxshape=(None,),                # (N,)
            )
        else:
            # positions
            d = f["positions"]
            d.resize(d.shape[0] + 1, axis=0)
            d[-1] = position

            # values
            d = f["values"]
            d.resize(d.shape[0] + 1, axis=0)
            d[-1] = values

            # timestamp
            d = f["timestamp"]
            d.resize(d.shape[0] + 1, axis=0)
            d[-1] = ts[0]


# ============================================================
# Measurement logic
# ============================================================

def run_measurement(position: list):
    """
    Called when model.hdf5 provides new candidates
    """
    y1 = target_function_1(position)
    y2 = target_function_2(position)

    values = y1 + y2

    print(f"[MEASUREMENT] x={position} -> y={values}")

    save_measurement(position, values)


def on_new_candidates(candidates: list):
    """
    candidates: list of positions [[x1, x2], [x1, x2], ...]
    """
    for pos in candidates:
        run_measurement(pos)


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    # Qt event loop needed for ModelWatcher
    app = QApplication([])

    # Optional server (still useful for later master integration)
    server = ServerLHC(
        address="tcp://*:1001",
        name="Measurement Server",
        device="OPT",
        freedom=2,
        data={}
    )
    server.start()

    # 👀 Watch model.hdf5
    watcher = ModelWatcher(SAVE_DIR)
    watcher.new_candidates.connect(on_new_candidates)

    try:
        app.exec()
    finally:
        server.stop()
