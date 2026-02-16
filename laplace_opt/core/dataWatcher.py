# core/dataWatcher.py
# to be implemented
import pathlib
import h5py
from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class DataWatcher(QObject):
    new_data_available = pyqtSignal()

    def __init__(self, folder: pathlib.Path, interval_ms: int = 1000, parent=None):
        super().__init__(parent)

        self.folder = folder
        self.data_file = folder / "measurements.hdf5"
        self._last_size = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._check_file)
        self.timer.start(interval_ms)

    def _check_file(self):
        if not self.data_file.exists():
            return

        try:
            with h5py.File(self.data_file, "r") as f:
                size = f["positions"].shape[0]
        except Exception:
            return  # file may be mid-write

        if size > self._last_size:
            self._last_size = size
            self.new_data_available.emit()
