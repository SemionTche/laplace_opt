# libraries
import sys
import logging

from PyQt6.QtWidgets import QApplication

from laplace_log import LoggerLHC, log
from laplace_server.protocol import LOGGER_NAME

# Initialize the logger
LoggerLHC("laplace.opt", file_level="debug", console_level="info")
log.info("Starting OptWindow...")

logging.getLogger(LOGGER_NAME).setLevel(logging.INFO)

# project
from .interface.optWindow import OptWindow

if __name__ == "__main__":
    app = QApplication(sys.argv) # create the app
    window = OptWindow()         # create the window
    window.show()                # display the window
    
    log.info("Window opened.")

    # end the process
    exit_code = app.exec()
    log.info(f"Application is exiting with code {exit_code}.")
    sys.exit(exit_code)