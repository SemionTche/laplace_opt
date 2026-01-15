# libraries
from PyQt6.QtWidgets import QApplication
import sys

from log_laplace.log_lhc import LoggerLHC, log

# Initialize the logger
LoggerLHC("opt_laplace", file_level="debug", console_level="info")
log.info("Starting OptWindow...")

# project
from interface.optWindow import OptWindow

if __name__ == "__main__":
    app = QApplication(sys.argv) # create the app
    window = OptWindow()         # create the window
    window.show()                # display the window
    
    log.debug("Window opened.")

    # end the process
    exit_code = app.exec()
    log.info(f"Application is exiting with code {exit_code}.")
    sys.exit(exit_code)