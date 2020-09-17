import sys
from PySide2.QtCore    import   Slot
from PySide2.QtWidgets import ( QApplication,
                                QAbstractItemView,
                                QListWidget,
                                QListWidgetItem,
                                QMenu)


class List(QListWidget):

    def __init__(self):
        super().__init__()
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)

        # Define actions and add them to menu
        print_items_action = context_menu.addAction('Print item(s)')
        rename_action      = context_menu.addAction('Rename item')

        # Connect actions to slots
        print_items_action.triggered.connect(self.__print_items_action())

        # Default behavior
        rename_action.setEnabled(False)

        # 0 item selected
        if not self.selectedItems():
            context_menu.setEnabled(False)

        # 1 item selected
        if len(self.selectedItems()) == 1:
            rename_action.setEnabled(True)
            print_items_action.setText('Print item')

        # Run menu
        context_menu.exec_(self.mapToGlobal(event.pos()))

    @Slot()
    def __print_items_action(self):
        for item in self.selectedItems():
            print(item.text())

    @Slot()
    def __rename_action(self, new_text: str):
        selected_item = self.selectedItems()[0]
        selected_item.setText(new_text)



if __name__ == '__main__':

    app = QApplication()

    list = List()
    list.addItems('Hey Beautiful Satanic Wagnerian'.split())
    list.show()

    sys.exit(app.exec_())
