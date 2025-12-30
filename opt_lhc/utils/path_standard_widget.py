# libraries
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, 
    QPushButton, QFileDialog,
)
from typing import Literal

import pathlib


class PathStandardWidget(QWidget):
    '''
    Widget made of a QLineEdit and a QPushButton in order
    to indicate a file or folder path. Allows to filter
    the available files.
    '''
    def __init__(self,
                 default: str = "",
                 button_title: str = "",
                 mode: Literal["file", "folder"] = "file",
                 file_filter: str = "All files (*)"):
        '''
            Args:
                default: (str)
                    the default path indicated in the QLineEdit.
                
                button_title: (str)
                    the label written on the button.
                
                mode: (str)
                    Either 'file' or 'folder', indicates the element
                    we are looking for.
                
                file_filter: (str)
                    indicate the files extension.
        '''
        super().__init__() # heritage from QWidget

        self.mode = mode
        self.file_filter = file_filter

        path_layout = QHBoxLayout(self)
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.setSpacing(8)

        self.path_line = QLineEdit(default)

        self.browse_button = QPushButton(button_title)
        self.browse_button.setFixedWidth(120)
        self.browse_button.setToolTip(
            "Select folder" if mode == "folder" else "Select file"
        )

        self.browse_button.clicked.connect(self.open_dialog)

        path_layout.addWidget(self.path_line)
        path_layout.addWidget(self.browse_button)


    def open_dialog(self) -> None:
        '''
        Define the QFileDialog to open depending
        on the 'mode' attribute.
        '''
        if self.mode == "folder":
            path = QFileDialog.getExistingDirectory(
                self,
                "Select folder",
                self.path_line.text()
            )
        else:
            path, _ = QFileDialog.getOpenFileName(
                self,
                "Select file",
                self.path_line.text(),
                filter=self.file_filter
            )

        if path:  # if a path is selected
            self.path_line.setText(path) # update the line

    ### helpers

    def text(self) -> str:
        return self.path_line.text()

    def setText(self, text: str):
        self.path_line.setText(text)

    def is_valid(self) -> bool:
        return pathlib.Path(self.text()).exists()
