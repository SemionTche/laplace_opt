# libraries
import sys
import logging

from PyQt6.QtWidgets import QApplication
from laplace_log import LoggerLHC, log
from laplace_server.protocol import LOGGER_NAME

# Initialize the logger
LoggerLHC(
    app_name="laplace.opt", 
    file_level="debug", 
    console_level="info"
)

# set the logging instances
logging.getLogger(LOGGER_NAME).setLevel(logging.INFO)       # from laplace-server
logging.getLogger("matplotlib").setLevel(logging.WARNING)   # from matplotlib
logging.getLogger("qdarkstyle").setLevel(logging.INFO)      # from qdarkstyle

from laplace_log import uncaught_exception    # import that allows to catch PyQt6 exceptions

# project
from .interface import OptWindow


if __name__ == "__main__":
    app = QApplication(sys.argv) # create the app
    window = OptWindow()         # create the window
    window.show()                # display the window
    
    log.info("Window opened.")

    # end the process
    exit_code = app.exec()
    log.info(f"Application is exiting with code {exit_code}.")
    sys.exit(exit_code)