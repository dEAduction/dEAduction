import sys
from PySide2.QtCore    import ( Qt,
                                Slot)
from PySide2.QtWidgets import ( QApplication,
                                QAbstractItemView,
                                QListWidget,
                                QListWidgetItem,
                                QMenu)


class List(QListWidget):

    def __init__(self):
        super().__init__()

class ListItem(QListWidgetItem):

    def __init__(self, text: str):
        super().__init__()

        self.setText(text)

        self.setFlags(self.flags() | Qt.ItemIsEditable)
        self.setData(Qt.ToolTipRole, 'Edit mode')

    def setData(self, role=None, value=None):
        super().setData(role, value)


if __name__ == '__main__':

    app = QApplication()

    list = List()
    list.addItem(ListItem('Computer'))
    list.addItem(ListItem('Filter'))
    list.show()

    sys.exit(app.exec_())
