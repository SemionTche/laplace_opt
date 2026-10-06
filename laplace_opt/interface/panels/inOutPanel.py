# librairies
from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, 
    QListWidget, QListWidgetItem
)

# project
from ..widgets import (
    InputWidget, ObjectiveWidget
)
from ...utils.getter import get_classes
from ...utils.model_source import ModelSource
from ...model_construction import (
    InputStructure, ObjectiveStructure
)

AVAILABLE_FOLDERS = ["inputs", "objectives"]

def verify_folder_name(folder_name) -> None:
    '''
    Check if the 'folder_name' attribute is among the
    available folder names. Otherwise raise an error.
    '''
    if folder_name not in AVAILABLE_FOLDERS:
        raise ValueError(
            f"folder_name '{folder_name}' argument" 
            f"must be chosen among '{AVAILABLE_FOLDERS}'."
        )


class InOutPanel(QGroupBox):
    '''
    Generic panel made to display inputs or objectives contained
    in the 'model_construction/inputs' or 'model_construction/objectives'
    folder.

    The classes contained in these folders are displayed using InputWidget 
    and ObjectiveWidget in a scrollable QListWidget.
    '''
    def __init__(self, folder_name: str, source: ModelSource):
        '''
        Arg:
            folder_name (str):
                The folder in 'model_construction' from
                which the classes must be extracted.
            
            source (ModelSource):
                Object storing the 'model_construction' 
                folder location
        '''
        verify_folder_name(folder_name)
        self.folder_name = folder_name
        self.source = source

        # define the widget type contained in the panel
        if folder_name == "inputs":
            self.widget_class = InputWidget
            super().__init__("Available Inputs")

        elif folder_name == "objectives":
            self.widget_class = ObjectiveWidget
            super().__init__("Available Objectives")

        # dictionary of the widgets stored in the InOutPanel
        self.rows: dict[str, InputWidget | ObjectiveWidget] = {}
            
        self.set_up()       # construct the list widget
        self.load_widgets() # add items to the list

    
    def set_up(self) -> None:
        '''Build the panel widgets.'''
        panel_layout = QVBoxLayout(self)          # create the layout
        self.list_widget = QListWidget()          # create the widget list
        panel_layout.addWidget(self.list_widget)  # add the widget list to the layout

    
    def load_widgets(self) -> None:
        '''
        Load the classes from 'folder_name' as 
        widgets and add them to the panel list.
        '''
        if self.folder_name == "inputs":
            items = get_classes(             # dict['class_name', class] contained in 'folder_name'
                dir=self.source.root, 
                category="inputs" 
            )  
        elif self.folder_name == "objectives":
            items = get_classes( 
                dir=self.source.root, 
                category="objectives" 
            )

        for name, cls in items.items():               # for each class
            
            new_widget = self.widget_class(name, cls) # define a new widget
            
            item = QListWidgetItem(self.list_widget)          # create a new list item
            item.setSizeHint(new_widget.sizeHint())           # set the size of the item
            self.list_widget.addItem(item)                    # add the new item in the list
            self.list_widget.setItemWidget(item, new_widget)  # assign the new widget to the item

            self.rows[name] = new_widget   # store the new widget in the dictionary


    ### helpers

    def enable_ip_port(self, enable: bool):
        '''
        Enable / disable all the InputWidget | ObjectiveWidget 
        ip:port of the panel.
        '''
        for widget in self.rows.values():                             # for every widget
            if isinstance(widget, (InputWidget, ObjectiveWidget)):    # if it is an 'InputWidget' or an 'ObjectiveWidget'
                widget.enable_ip_port(enable)                         # enable / disable the ip:port and position index


    ### getters
    def get_rows(self) -> dict[str, InputWidget | ObjectiveWidget]:
        '''Return the widgets stored in the panel.'''
        return self.rows

    def get_enabled_rows(self) -> dict[str, InputStructure | ObjectiveStructure]:
        '''Return the selected widgets of the panel.'''
        enabled = {}
        for name, widget in self.rows.items():     # for every widget
            if widget.is_enabled():                # if the widget is selected
                enabled[name] = widget.instance    # add it to the dictionary
        return enabled

