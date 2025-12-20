# libraries
from PyQt6.QtWidgets import QApplication
import sys

# project
from interface.optWindow import OptWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OptWindow()
    window.show()
    sys.exit(app.exec())