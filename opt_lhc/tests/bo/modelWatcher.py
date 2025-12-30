# measurement/modelWatcher.py
import pathlib
import h5py
from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class ModelWatcher(QObject):
    new_candidates = pyqtSignal(list)

    def __init__(self, folder: pathlib.Path, interval_ms=1000, parent=None):
        super().__init__(parent)
        self.file = folder / "model.hdf5"
        self.last_step = -1

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._check)
        self.timer.start(interval_ms)

    def _check(self):
        if not self.file.exists():
            return

        try:
            with h5py.File(self.file, "r") as f:
                step = int(f["step"][()])
                if step == self.last_step:
                    return

                X_next = f["next_candidates"][:]
        except Exception:
            return

        self.last_step = step
        self.new_candidates.emit(X_next.tolist())
