from functools import partial
import sys
from typing import    Callable

from PySide2.QtCore    import ( Qt,
                                Slot)
from PySide2.QtWidgets import ( QAction,
                                QApplication,
                                QAbstractItemView,
                                QListWidget,
                                QListWidgetItem,
                                QMenu )


class MyAction(QAction):

    def __init__(self, title: str, slot: Callable):

        super().__init__()
        self.setText(title)

        self.__slot = slot

    @property
    def slot(self) -> Callable:

        return self.__slot


class MyMenu(QMenu):

    def __init__(self, actions: [MyAction], selection_function: Callable):

        super().__init__()

        @Slot()
        def slut(action):
            action.slot(selection_function())

        for action in actions:
            action.triggered.connect(partial(slut, action))
            self.addAction(action)


class MyList(QListWidget):

    def __init__(self):

        super().__init__()

        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # Context menu
        self.__context_menu = MyMenu(ACTIONS, self.selection)

    def selection(self):

        return self.selectedItems()

    def contextMenuEvent(self, event):
        self.__context_menu.exec_(self.mapToGlobal(event.pos()))


ACTION_1 = MyAction('Print selection', lambda selection: print(len(selection), [x.text() for x in selection]))
ACTION_2 = MyAction('Go fuck yourself', lambda x: print('Go fuck yourself'))
ACTIONS = [ACTION_1, ACTION_2]


if __name__ == '__main__':

    app = QApplication()

    my_list = MyList()
    my_list.addItem(QListWidgetItem('Gulli good'))
    my_list.addItem(QListWidgetItem('Computer'))
    my_list.addItem(QListWidgetItem('Filter'))
    my_list.addItem(QListWidgetItem('Happier'))
    my_list.addItem(QListWidgetItem('Obscured by clouds'))
    my_list.show()

    sys.exit(app.exec_())
