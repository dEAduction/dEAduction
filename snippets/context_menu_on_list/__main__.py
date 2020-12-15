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
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def contextMenuEvent(self, event):
        cmenu = QMenu(self)

        # Define actions and add them to menu
        print_items_action = cmenu.addAction('Print item(s)')

        # Connect actions to slots
        print_items_action.triggered.connect(self.__print_items_action)

        # Default behavior

        # 0 item selected
        if not self.selectedItems():
            cmenu.setEnabled(False)

        # 1 item selected
        if len(self.selectedItems()) == 1:
            print_items_action.setText('Print item')

        # Run menu
        cmenu.exec_(self.mapToGlobal(event.pos()))

    @Slot()
    def __print_items_action(self):
        for item in self.selectedItems():
            print(item.text)


if __name__ == '__main__':

    logger.configure()

    app = QApplication()

    list = List()
    list.addItem(QListWidgetItem('Computer'))
    list.addItem(QListWidgetItem('Filter'))
    list.addItem(QListWidgetItem('Happier'))
    list.addItem(QListWidgetItem('Obscured by clouds'))
    list.show()

    sys.exit(app.exec_())
