# libraries
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QCheckBox, QLabel, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

import pathlib

# project
from model_construction.objectives.objective_structure import ObjectiveStructure

class ObjectiveWidget(QWidget):
    '''
    ObjectiveWidget defines the line of an objective. The objective 
    must have it's own class file in 'model_construction/objectives' 
    and respect the 'ObjectiveStructure' format.
    '''
    def __init__(self, name: str, cls: type[ObjectiveStructure]):
        '''
            Args:
                name: (str)
                    name of the class used for this line.

                cls: (type)
                    the class of the objective.
        '''
        super().__init__() # heritage from QWidget

        self.name = name
        self.instance: ObjectiveStructure = cls()  # make an instance

        # main objective line layout
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
        self.state_checkBox.setToolTip(f"Include objective '{name}' in config")
        self.state_checkBox.setFixedWidth(20)
        line_layout.addWidget(self.state_checkBox)

        # state icon
        self.state_icon = QLabel() # create a blank label
        self.state_icon.setFixedWidth(20)
        self.state_icon.setPixmap(self.disconnected_icon.pixmap(16, 16)) # add an image
        line_layout.addWidget(self.state_icon)

        # name label
        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        line_layout.addWidget(self.name_label)

        # minimize/maximize selector
        self.mode = QComboBox()
        self.mode.addItems(["Minimize", "Maximize"])
        self.mode.setToolTip("Choose whether to minimize or maximize this objective")
        line_layout.addWidget(self.mode)

        # defines the default combo box display
        if self.instance.minimize is False:
            self.mode.setCurrentIndex(1)  # set maximize

        self.mode.setEnabled(False)  # disabled by default

        self.actions() # defines the class actions


    def actions(self) -> None:
        '''
        Defines the actions of ObjectiveWidget class.
        '''
        # when the state changes, enable / disable the mode and change the icon
        self.state_checkBox.stateChanged.connect(self.on_state_changed)
        
        # when the mode changes, update the instance
        self.mode.currentTextChanged.connect(self.on_mode_changed)


    def on_state_changed(self, enabled: bool) -> None:
        '''
        When the ObjectiveWidget state changes, enable / disable
        the mode combo box and change the icon.
        '''        
        # change the icon
        icon = self.connected_icon if enabled else self.disconnected_icon
        self.state_icon.setPixmap(icon.pixmap(16, 16))

        self.mode.setEnabled(enabled)


    def on_mode_changed(self) -> None:
        '''
        Update the instance when the user selects Minimize/Maximize.
        '''
        if self.is_minimize():
            self.instance.set_minimize(True)
        else:
            self.instance.set_minimize(False)

    ### helpers

    def is_enabled(self) -> bool:
        return self.state_checkBox.isChecked()

    def is_minimize(self) -> bool:
        return self.mode.currentText() == "Minimize"