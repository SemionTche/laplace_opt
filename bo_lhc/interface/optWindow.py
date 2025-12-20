from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QGridLayout,
    QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QSettings, QTimer
from PyQt6.QtGui import QIcon

import qdarkstyle
import pathlib
import os

class OptWindow(QMainWindow):
    
    def __init__(self):

        super().__init__() # heritage from QMainWindow

        # Set window title
        self.setWindowTitle("Master Window")
        p = pathlib.Path(__file__)
        sepa = os.sep
        self.icon = str(p.parent) + sepa + 'icons' + sepa

        # self.settings = QSettings(str(p.parent / "interface.ini"), QSettings.Format.IniFormat)

        self.setWindowIcon(QIcon(self.icon+'LOA.png'))
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        self.setGeometry(100, 30, 1000, 700)