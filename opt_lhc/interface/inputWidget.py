# libraries
from typing import Optional, Tuple
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QCheckBox, QLabel, QDoubleSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

import pathlib

# project
from utils.getter import get_from_cls

class InputWidget(QWidget):
    '''
    InputWidget defines the line of an input. The input must 
    have it's own class file in 'model_construction/inputs' 
    and respect the InputStructure format.
    '''
    def __init__(self, name: str, cls: type):
        '''
            Args:
                name: (str)
                    name of the class used for this line.

                cls: (type)
                    the class of the inout.
        '''
        super().__init__() # heritage from QWidget
        
        self.name = name
        self.cls = cls

        # main input line layout
        line_layout = QHBoxLayout(self)
        line_layout.setContentsMargins(4, 2, 4, 2)
        line_layout.setSpacing(8)
        self.setLayout(line_layout)

        p = pathlib.Path(__file__)       # get the path of the file
        icon_path = p.parent / 'icons'   # path to the icon folder

        # build the check and uncheck icons
        self.connected_icon = QIcon(str(icon_path / 'connected.png'))
        self.disconnected_icon = QIcon(str(icon_path / 'disconnected.png'))

        # state
        self.state_checkBox = QCheckBox()
        self.state_checkBox.setToolTip(f"Enable {name}")
        self.state_checkBox.setFixedWidth(20)
        line_layout.addWidget(self.state_checkBox)

        # state icon
        self.state_icon = QLabel() # create a blank label
        self.state_icon.setFixedWidth(20)
        self.state_icon.setPixmap(self.disconnected_icon.pixmap(16, 16)) # add an image
        line_layout.addWidget(self.state_icon)

        # address
        self.address_label = QLabel("Unkown")
        address = get_from_cls(self.cls, "address") # get address from the class
        self.address = str(address) if address is not None else None
        if self.address:
            self.address_label.setText(self.address)
        self.address_label.setEnabled(False)
        line_layout.addWidget(self.address_label)

        # name
        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        line_layout.addWidget(self.name_label)

        # Min spinBox
        self.min_spin = QDoubleSpinBox()
        self.min_spin.setDecimals(6)
        self.min_spin.setEnabled(False)
        line_layout.addWidget(self.min_spin)

        # Max spinBox
        self.max_spin = QDoubleSpinBox()
        self.max_spin.setDecimals(6)
        self.max_spin.setEnabled(False)
        line_layout.addWidget(self.max_spin)

        # Unit
        self.unit_label = QLabel("Unknown")
        unit = get_from_cls(self.cls, "unit") # get unit from the class
        self.unit = str(unit) if unit is not None else None
        if self.unit:
            self.unit_label.setText(self.unit)
            self.unit_label.setFixedWidth(25)
            self.unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        line_layout.addWidget(self.unit_label)

        # Safe bounds
        self.safe_label = QLabel("safe: n/a")
        self.safe_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.safe_label.setFixedWidth(100)
        line_layout.addWidget(self.safe_label)

        sb = get_from_cls(self.cls, "safe_bounds") # get safe bounds from the class

        self.safe_bounds = tuple(sb) if sb is not None else None
        if self.safe_bounds:
            safe_lo, safe_hi = self.safe_bounds
            # min spin
            self.min_spin.setMinimum(safe_lo)
            self.min_spin.setMaximum(safe_hi)
            self.min_spin.setValue(safe_lo)
            # max spin
            self.max_spin.setMinimum(safe_lo)
            self.max_spin.setMaximum(safe_hi)
            self.max_spin.setValue(safe_hi)
            # set label safe bounds
            self.safe_label.setText(f"safe: {self.safe_bounds}")

        self.actions() # defines the actions of InputWidget


    def actions(self) -> None:
        '''
        Defines the actions of the InputWidget class.
        '''
        # when the state is changed, change the icon and enable / disable the spin boxes
        self.state_checkBox.stateChanged.connect(self.on_state_changed)
        # when the spin boxes are updated, verify the safe bounds
        self.min_spin.valueChanged.connect(self.safe_bounds_checking)
        self.max_spin.valueChanged.connect(self.safe_bounds_checking)


    def on_state_changed(self, enabled: bool) -> None:
        '''
        When the InputWidget state changes, enable / disable
        the spin boxes, change the icon and check the bounds.
        '''
        # change the icon
        icon = self.connected_icon if enabled else self.disconnected_icon
        self.state_icon.setPixmap(icon.pixmap(16, 16))

        self.min_spin.setEnabled(enabled)  # enable / disable the spin boxes
        self.max_spin.setEnabled(enabled)

        if not enabled:
            # reset the style of the widget (disable colors)
            self.min_spin.setStyleSheet("")
            self.max_spin.setStyleSheet("")
            self.safe_label.setStyleSheet("")
        
        self.safe_bounds_checking() # verify if the spin boxes are valid.


    def safe_bounds_checking(self) -> None:
        '''
        Verify the boundaries provided in the spin boxes.
        Update safe bounds label accordingly.
        '''
        # if the InputWidget is not selected
        if not self.state_checkBox.isChecked():
            return  # do not check the boundaries
        
        valid = True
        sb = self.get_value() # get the spin box values
        
        if sb is None: # if there is no safe bounds
            valid = False # the format is invalid

        # Update styles
        if not valid:
            # add red over the spin boxes
            self.min_spin.setStyleSheet("border: 1px solid red;")
            self.max_spin.setStyleSheet("border: 1px solid red;")
            self.safe_label.setStyleSheet("color: red;") # set the safe bound red color
        else:
            # reset the spin boxe styles (disable the color)
            self.min_spin.setStyleSheet("")
            self.max_spin.setStyleSheet("")
            self.safe_label.setStyleSheet("color: green;") # set the safe bound green color


    def get_value(self) -> Optional[Tuple[float, float]]:
        '''
        Return the values of the spin boxes if they are in the safe boundaries.
        Return None otherwise.
        '''
        if not self.state_checkBox.isChecked(): # if the InputWidget is not selected
            return None
        
        lo = self.min_spin.value() # get the spin box values
        hi = self.max_spin.value()
        
        if self.safe_bounds: # if the safe bounds exist
            safe_lo, safe_hi = self.safe_bounds
            if lo < safe_lo or hi > safe_hi or lo >= hi: # compare the corresponding boundaries
                return None

        return (lo, hi)

    ### helpers

    def is_enabled(self) -> bool:
        return self.state_checkBox.isChecked()

    def enable_address(self, enable: bool) -> None:
        self.address_label.setEnabled(enable)
