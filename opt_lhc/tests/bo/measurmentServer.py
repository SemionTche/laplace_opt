import pathlib
import time
import h5py
import numpy as np

from target_function_1 import target_function_1
from target_function_2 import target_function_2

from server_lhc.serverLHC import ServerLHC
from server_lhc.serverController import ServerController


# ============================================================
# Storage
# ============================================================

SAVE_DIR = pathlib.Path("save")
SAVE_DIR.mkdir(exist_ok=True)

H5_FILE = SAVE_DIR / "measurements.h5"


def save_measurement(position, values):
    position = np.asarray(position, dtype=float)
    values = np.asarray(values, dtype=float)

    with h5py.File(H5_FILE, "a") as f:
        if "positions" not in f:
            f.create_dataset("positions", data=position[None, :],
                             maxshape=(None, position.size))
            f.create_dataset("values", data=values[None, :],
                             maxshape=(None, values.size))
            f.create_dataset("timestamp", data=[time.time()],
                             maxshape=(None,))
        else:
            for name, data in {
                "positions": position,
                "values": values,
                "timestamp": np.array(time.time())
            }.items():
                dset = f[name]
                dset.resize((dset.shape[0] + 1), axis=0)
                dset[-1] = data


# ============================================================
# Measurement logic
# ============================================================

def new_measurement(positions: list):
    """
    Called when SET is received by the server
    """
    y1 = target_function_1(positions)
    y2 = target_function_2(positions)

    values = y1 + y2  # concatenate objectives

    print(f"[MEASUREMENT] x={positions} -> y={values}")

    save_measurement(positions, values)


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    server = ServerLHC(
        address="tcp://*:1001",
        name="Test Optimizer",
        device="OPT",
        freedom=2,
        data={}
    )

    controller = ServerController()
    server.on_position_changed = controller.on_position_changed
    controller.position_changed.connect(new_measurement)

    server.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
