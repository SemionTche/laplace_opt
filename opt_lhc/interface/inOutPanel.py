# librairies
from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QListWidget, QListWidgetItem

# project
from interface.inputWidget import InputWidget
from interface.objectiveWidget import ObjectiveWidget

from utils.getter import get_classes
from model_construction.inputs.input_structure import InputStructure
from model_construction.objectives.objective_structure import ObjectiveStructure

class InOutPanel(QGroupBox):
    '''
    Generic panel made to display inputs or objectives contained
    in the 'model_construction/inputs' or 'model_construction/objectives'
    folder.

    Displaying the classes contained in these folders using InputWidget and 
    ObjectiveWidget in a scrollable QListWidget.
    '''
    def __init__(self, title: str, folder_name: str):
        '''
            Args:
                title: (str)
                    the title of the Group Box.
                
                folder_name: (str)
                    the folder in 'model_construction' from
                    which the classes must be extracted.
        '''
        super().__init__(title)  # heritage from QGroupBox

        self.folder_name = folder_name
        self.verify_folder_name() # verify the folder_name

        # define the widget type contained in the panel
        self.widget_class = None
        if folder_name == "inputs":
            self.widget_class = InputWidget
        elif folder_name == "objectives":
            self.widget_class = ObjectiveWidget
        else:
            raise TypeError("The class widget could not be found.")

        # dictionary of the widgets stored in the InOutPanel
        self.rows: dict[str, InputWidget | ObjectiveWidget] = {}
            
        self.set_up() # construct the list widget
        self.load_widgets() # add items to the list

    
    def set_up(self) -> None:
        '''
        Build the panel main widgets.
        '''
        panel_layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        panel_layout.addWidget(self.list_widget)

    
    def load_widgets(self) -> None:
        '''
        Load the classes from folder_name attribute as 
        widgets and add them to the panel list.
        '''
        items = get_classes(self.folder_name) # dict[class_name, class] contained in 'folder_name'

        for name, cls in items.items(): # for each class
            
            new_widget = self.widget_class(name, cls) # define a new widget
            
            item = QListWidgetItem(self.list_widget)         # create a new list item
            item.setSizeHint(new_widget.sizeHint())          # set the size of the item
            self.list_widget.addItem(item)                   # add the new item
            self.list_widget.setItemWidget(item, new_widget) # assign new widget to item

            self.rows[name] = new_widget   # store the new widget in the dictionary
    

    def verify_folder_name(self) -> None:
        '''
        Checks if the folder_name attribute is among the
        available folder names. Otherwise raise an error.
        '''
        available_folders = ["inputs", "objectives"]
        if self.folder_name not in available_folders:
            raise ValueError(
                f"folder_name '{self.folder_name}' argument must be chosen among '{available_folders}'."
            )

    ### helpers

    def enable_addresses(self, enable: bool):
        '''
        Enable / disable all the InputWidget addresses
        of the panel.
        '''
        for widget in self.rows.values():
            if isinstance(widget, (InputWidget, ObjectiveWidget)):
                widget.enable_address(enable)

    def get_rows(self) -> dict[str, InputWidget | ObjectiveWidget]:
        return self.rows

    def get_enabled_rows(self) -> dict[str, InputStructure | ObjectiveStructure]:
        enabled = {}
        for name, widget in self.rows.items():
            if widget.is_enabled():
                enabled[name] = widget.instance
        return enabled

