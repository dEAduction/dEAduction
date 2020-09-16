import sys
from PySide2.QtCore    import   Slot
from PySide2.QtWidgets import ( QApplication,
                                QListWidget,
                                QListWidgetItem,
                                QMenu)


class List(QListWidget):

    def __init__(self):
        super().__init__()

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)

        # Define actions and add them to menu
        print_items_action = context_menu.addAction('Print item(s)')

        # Connect actions to slots
        print_items_action.triggered.connect(self.print_items())

        # Run menu
        context_menu.exec_(self.mapToGlobal(event.pos()))

    @Slot()
    def print_items(self):
        for item in self.selectedItems():
            print(item.text())



if __name__ == '__main__':

    app = QApplication()

    list = List()
    list.addItems('Hey Beautiful Satanic Wagnerian'.split())
    list.show()

    sys.exit(app.exec_())
