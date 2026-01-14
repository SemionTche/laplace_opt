# libraries
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QCheckBox, QLabel, QDoubleSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

import pathlib

# project
from model_construction.inputs.input_structure import InputStructure

class InputWidget(QWidget):
    '''
    InputWidget defines the line of an input. The input must 
    have its own class file in 'model_construction/inputs' 
    and respect the InputStructure format.
    '''
    def __init__(self, name: str, cls: type[InputStructure]):
        '''
            Args:
                name: (str)
                    name of the class used for this line.

                cls: (type)
                    the class of the input. 
                    (must heritate from 'InputStructure')
        '''
        super().__init__() # heritage from QWidget
        
        self.name = name
        self.instance: InputStructure = cls()  # create a class instance

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
        self.state_icon.setToolTip("Current state")
        line_layout.addWidget(self.state_icon)

        # address
        self.address_label = QLabel()
        self.address = self.instance.address      # get address from the instance
        self.address_label.setText(self.address or "Unknown")
        self.address_label.setEnabled(False)
        self.address_label.setToolTip("The address of the input device used by the server")
        line_layout.addWidget(self.address_label)

        # position index
        self.position_label = QLabel()
        self.position_index = self.instance.position_index
        self.position_label.setText(str(self.position_index) or "Unknown")
        self.position_label.setEnabled(False)
        self.position_label.setFixedWidth(20)
        self.position_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.position_label.setToolTip("The position of the input device in the server list")
        line_layout.addWidget(self.position_label)

        # name
        self.name_label = QLabel(name)
        self.tip = self.instance.description
        self.name_label.setToolTip(self.tip)    # add a description
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
        self.unit = self.instance.unit   # get unit from the instance
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

        self.safe_bounds = self.instance.safe_bounds   # get safe bounds from the instance

        if self.safe_bounds:
            safe_lo, safe_hi = self.safe_bounds
            self.min_spin.setRange(safe_lo, safe_hi)
            self.max_spin.setRange(safe_lo, safe_hi)

        lo, hi = self._compute_effective_bounds()

        self.min_spin.setValue(lo)
        self.max_spin.setValue(hi)

        self.instance.set_bounds((lo, hi))
        
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
        
        self.min_spin.valueChanged.connect(self.update_instance_bounds)
        self.max_spin.valueChanged.connect(self.update_instance_bounds)


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


    def update_instance_bounds(self) -> None:
        '''
        Update the bounds in the class instance.
        '''
        if not self.is_enabled():
            return

        bounds = self.get_value()
        if bounds is not None:
            self.instance.set_bounds(bounds)


    def _compute_effective_bounds(self) -> tuple[float, float]:
        """
        Compute the bounds actually used by the UI and the instance,
        intersecting instance.bounds with safe_bounds if needed.
        """
        lo, hi = self.instance.bounds

        if self.safe_bounds:
            safe_lo, safe_hi = self.safe_bounds
            lo = max(lo, safe_lo)
            hi = min(hi, safe_hi)

        if lo >= hi:
            raise ValueError(
                f"Invalid bounds after applying safe bounds for {self.name}: "
                f"{(lo, hi)}"
            )

        return lo, hi


    def safe_bounds_checking(self) -> None:
        '''
        Verify the boundaries provided in the spin boxes.
        Update safe bounds label accordingly.
        '''
        # if the InputWidget is not selected
        if not self.is_enabled():
            return  # do not check the boundaries

        valid = self.get_value() is not None

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


    def get_value(self) -> tuple[float, float] | None:
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
        self.position_label.setEnabled(enable)
