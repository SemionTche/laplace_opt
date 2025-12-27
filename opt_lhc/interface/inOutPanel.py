from typing import Dict, Type
from PyQt6.QtWidgets import QWidget, QGroupBox, QVBoxLayout, QListWidget, QListWidgetItem
from utils.getter import get_classes


class InOutPanel(QGroupBox):
    """
    Generic panel that can display a list of row widgets (InputRow, ObjectiveRow, etc.)
    in a scrollable QListWidget.
    """

    def __init__(self, title: str, row_class: Type[QWidget], get_classes_type: str = None, parent=None):
        """
        :param title: QGroupBox title
        :param row_class: class to instantiate for each row (InputRow or ObjectiveRow)
        :param get_classes_type: if provided, will call get_classes(get_classes_type)
        :param parent: optional parent widget
        """
        super().__init__(title, parent)

        self.row_class = row_class
        self.rows: Dict[str, QWidget] = {}

        self._build_ui()
        self._populate_rows(get_classes_type)

    # ------------------------ UI ------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

    # ------------------------ Populate ------------------------
    def _populate_rows(self, get_classes_type: str = None):
        if get_classes_type:
            items = get_classes(get_classes_type)  # returns dict[name, class]
        else:
            # row_class handles creation itself, for ObjectiveRow
            items = {row_class.__name__: self.row_class for row_class in []}

        for name, cls in items.items():
            if get_classes_type:
                try :
                    row = self.row_class(name, cls)
                except TypeError:
                    # fallback for ObjectiveRow
                    row = self.row_class(name)

            self.rows[name] = row

            # Wrap in QListWidgetItem
            item = QListWidgetItem(self.list_widget)
            item.setSizeHint(row.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, row)

    # ------------------------ API ------------------------
    def get_rows(self) -> Dict[str, QWidget]:
        """Return dictionary of name -> row widget"""
        return self.rows
