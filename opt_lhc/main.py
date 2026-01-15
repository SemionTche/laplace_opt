# libraries
from PyQt6.QtWidgets import QApplication
import sys

from log_laplace.log_lhc import LoggerLHC

logger = LoggerLHC("opt_laplace")
logger.info("Hello from Laplace logger!")

# project
from interface.optWindow import OptWindow

if __name__ == "__main__":
    app = QApplication(sys.argv) # create the app
    window = OptWindow()         # create the window
    window.show()                # display it
    sys.exit(app.exec())         # end the process