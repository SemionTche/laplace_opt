# libraries
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QCheckBox, QLabel, QDoubleSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

import pathlib

from log_laplace.log_lhc import log

# project
from model_construction.inputs.input_structure import InputStructure


class InputWidget(QWidget):
    '''
    Define the input line. The input must have its own 
    class file in 'model_construction/inputs' and respect 
    the InputStructure format.
    '''
    def __init__(self, name: str, cls: type[InputStructure]):
        '''
            Args:
                name: (str)
                    class name used for this line.

                cls: (type)
                    the input class. 
                    (must heritate from 'InputStructure')
        '''
        super().__init__() # heritage from QWidget
        
        self.name = name
        self.instance: InputStructure = cls()  # create a class instance

        # get relevant features from the instance
        self.address = self.instance.address
        self.position_index = self.instance.position_index
        self.description = self.instance.description
        self.unit = self.instance.unit
        self.safe_bounds = self.instance.safe_bounds

        self.set_up()  # build the input widget
        self.actions() # defines the actions of InputWidget

        # first verification of the boundaries
        self.set_inital_boundaries()  # compare the default input boundaries with the safe ones
        self.update_min_max()


    def set_up(self) -> None:
        '''
        Build the widgets inside InputWidget.
        '''
        # input line layout
        line_layout = QHBoxLayout(self)
        line_layout.setContentsMargins(4, 2, 4, 2) # widget margin
        line_layout.setSpacing(8)                  # spacing
        self.setLayout(line_layout)                # set layout

        p = pathlib.Path(__file__)              # get the file path
        icon_path = p.parent.parent / 'icons'   # get the icon folder path

        # build the check and uncheck icons
        self.connected_icon = QIcon(str(icon_path / 'connected.png'))
        self.disconnected_icon = QIcon(str(icon_path / 'disconnected.png'))

        # state
        self.state_checkBox = QCheckBox()
        self.state_checkBox.setToolTip(f"Include input '{self.name}' in config")
        self.state_checkBox.setFixedWidth(20)
        line_layout.addWidget(self.state_checkBox)

        # state icon
        self.state_icon = QLabel()                                       # create a blank label
        self.state_icon.setFixedWidth(20)
        self.state_icon.setPixmap(self.disconnected_icon.pixmap(16, 16)) # add an image
        self.state_icon.setToolTip("Current state")
        line_layout.addWidget(self.state_icon)

        # address
        self.address_label = QLabel()
        self.address_label.setText(self.address or "Unknown")
        self.address_label.setEnabled(False)
        self.address_label.setToolTip("The address of the input device used by the server")
        line_layout.addWidget(self.address_label)

        # position index
        self.position_label = QLabel()
        self.position_label.setText(str(self.position_index) or "Unknown")
        self.position_label.setEnabled(False)
        self.position_label.setFixedWidth(20)
        self.position_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.position_label.setToolTip("The position of the input device in the server list")
        line_layout.addWidget(self.position_label)

        # name
        self.name_label = QLabel(self.name)
        self.name_label.setToolTip(self.description)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        line_layout.addWidget(self.name_label)

        # Min spinBox
        self.min_spin = QDoubleSpinBox()
        self.min_spin.setDecimals(6)
        self.min_spin.setEnabled(False)
        self.min_spin.setToolTip("Minimal boundary")
        line_layout.addWidget(self.min_spin)

        # Max spinBox
        self.max_spin = QDoubleSpinBox()
        self.max_spin.setDecimals(6)
        self.max_spin.setEnabled(False)
        self.max_spin.setToolTip("Maximal boundary")
        line_layout.addWidget(self.max_spin)

        # Unit
        self.unit_label = QLabel()
        self.unit_label.setText(self.unit or "Unknown")
        self.unit_label.setFixedWidth(25)
        self.unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unit_label.setToolTip("Input unit")
        line_layout.addWidget(self.unit_label)

        # Safe bounds
        self.safe_label = QLabel("safe: n/a")
        self.safe_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.safe_label.setFixedWidth(100)
        self.safe_label.setToolTip("The intervalle available")
        line_layout.addWidget(self.safe_label)

        safe_lo, safe_hi = self.safe_bounds
        self.min_spin.setRange(safe_lo, safe_hi)
        self.max_spin.setRange(safe_lo, safe_hi)
        
        # set label safe bounds
        self.safe_label.setText(f"safe: {self.safe_bounds}")
        self.safe_label.setEnabled(False)


    def actions(self) -> None:
        '''
        Defines the actions of the InputWidget class.
        '''
        # when the input state is changed, change the icon and enable / disable the spin boxes
        self.state_checkBox.stateChanged.connect(self.on_state_changed)
        
        # when the spin boxes are updated, change the input instance boundaries
        self.min_spin.valueChanged.connect(self.update_instance_bounds)
        self.max_spin.valueChanged.connect(self.update_instance_bounds)

        # when the spin boxes are updated, change the spin boxes range
        self.min_spin.valueChanged.connect(self.update_min_max)
        self.max_spin.valueChanged.connect(self.update_min_max)


    def set_inital_boundaries(self) -> None:
        '''
        Compare the default and safe boundaries and set it 
        in the instance.
        
        Set the spin boxes initial values. 
        '''
        lo, hi = self.instance.bounds
        safe_lo, safe_hi = self.instance.safe_bounds
    
        lo = max(lo, safe_lo)
        hi = min(hi, safe_hi)

        self.instance.set_bounds((lo, hi))  # set the instance boundaries

        # set the spin boxe values
        self.min_spin.setValue(lo)
        self.max_spin.setValue(hi)


    def on_state_changed(self, enabled: bool) -> None:
        '''
        When the InputWidget state change, enable / disable
        the spin boxes, change the icon and check the boundaries.
        '''
        # change the icon
        icon = self.connected_icon if enabled else self.disconnected_icon
        self.state_icon.setPixmap(icon.pixmap(16, 16))

        self.min_spin.setEnabled(enabled)  # enable / disable the spin boxes
        self.max_spin.setEnabled(enabled)

        self.safe_label.setEnabled(enabled) # enable / disable safe label
        log.debug(f"Input '{self.name}' added." if enabled else f"Input '{self.name}' removed.")


    def update_instance_bounds(self) -> None:
        '''
        Update the boundaries in the class instance.
        '''
        if not self.is_enabled():  # if the input is not selected
            return                 # do not change anything

        bounds = self.get_value()            # get the boundary values
        if bounds is not None:               # if the value is valid
            self.instance.set_bounds(bounds) # update the instance boundaries
            log.debug(f"Input '{self.name}' boundaries changed, new boundaries = {bounds}")


    def update_min_max(self) -> None:
        '''
        Update the min and max values of the spin boxes.
        '''
        safe_lo, safe_hi = self.safe_bounds
        self.min_spin.setRange(safe_lo, self.max_spin.value())
        self.max_spin.setRange(self.min_spin.value(), safe_hi)


    def get_value(self) -> tuple[float, float] | None:
        '''
        Return the spin boxe's values if they are in the safe boundaries.
        Return None otherwise.
        '''
        if not self.state_checkBox.isChecked(): # if the InputWidget is not selected
            return None                         # do nothing
        
        lo = self.min_spin.value() # get the spin box values
        hi = self.max_spin.value()

        safe_lo, safe_hi = self.safe_bounds  # get the safe bounds

        valid = safe_lo <= lo <= hi <= safe_hi  # define if valid

        if not valid:
            return None

        return (lo, hi)


    ### helpers

    def is_enabled(self) -> bool:
        return self.state_checkBox.isChecked()

    def enable_address(self, enable: bool) -> None:
        '''Enable / disable the 'address' and 'position_index' fields.'''
        self.address_label.setEnabled(enable)
        self.position_label.setEnabled(enable)