import logging
import sys

from PySide2.QtCore    import ( Qt,
                                Slot)
from PySide2.QtWidgets import ( QApplication,
                                QAbstractItemView,
                                QListWidget,
                                QListWidgetItem,
                                QMenu)

from deaduction.pylib import logger as logger

log = logging.getLogger('')


class List(QListWidget):

    def __init__(self):
        super().__init__()
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.itemDoubleClicked.connect(self.__rename_item_action)

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)

        # Define actions and add them to menu
        print_items_action = context_menu.addAction('Print item(s)')
        rename_item_action = context_menu.addAction('Rename item')

        # Connect actions to slots
        print_items_action.triggered.connect(self.__print_items_action)
        rename_item_action.triggered.connect(self.__rename_item_action)

        # Default behavior
        rename_item_action.setEnabled(False)

        # 0 item selected
        if not self.selectedItems():
            context_menu.setEnabled(False)

        # 1 item selected
        if len(self.selectedItems()) == 1:
            rename_item_action.setEnabled(True)
            print_items_action.setText('Print item')

        # Run menu
        context_menu.exec_(self.mapToGlobal(event.pos()))

    @Slot()
    def __print_items_action(self):
        for item in self.selectedItems():
            print(item.text)

    @Slot()
    def __rename_item_action(self):
        log.debug('List.__rename_item_action called')

        item = self.selectedItems()[0]
        item.setData(Qt.EditRole, 'Change item name')
        log.debug(f'item.text after setData(Qt.EditRole, …): {item.text}')

        self.editItem(item)


class ListItem(QListWidgetItem):

    def __init__(self, name: str, text: str):
        super().__init__()

        self.setFlags(self.flags() | Qt.ItemIsEditable)

        self.name = name
        self.text = text

        self.__set_name_text()

    def change_name(self, new_name: str):
        self.name = new_name
        self.__set_name_text()

    def __set_name_text(self):
        self.setText(f'{self.name} : {self.text}')

if __name__ == '__main__':

    logger.configure()

    app = QApplication()

    list = List()
    list.addItem(ListItem('1', 'Computer'))
    list.addItem(ListItem('2', 'Filter'))
    list.show()

    sys.exit(app.exec_())
