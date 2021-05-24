# Context menus for class MathObjectWidget

import sys
from typing import Callable

from PySide2.QtWidgets import (QListWidget,
                               QListWidgetItem,
                               QAbstractItemView,
                               QApplication,
                               QMainWindow,
                               QMenu,
                               QAction)


class MathObject(QListWidgetItem):
    def __init__(self, text: str):
        super().__init__()
        self.setText(text)


class ContextMenuAction(QAction):
    def __init__(self, text: str, is_available: Callable[[MathObject], bool]):
        super().__init__()
        self.setText(text)
        self.is_available = is_available


class ContextMenu(QMenu):
    def __init__(self, actions: [ContextMenuAction]):
        super().__init__()
        self.actions = actions
        for action in actions:
            self.addAction(action)

    def set_availability(self, current_selection: [MathObject]):
        for action in self.actions:
            if action.is_available(current_selection):
                action.setEnabled(True)
            else:
                action.setEnabled(False)


class MathObjectWidget(QListWidget):
    def __init__(self, math_objects: [MathObject]):
        super().__init__()
        self.math_objects = math_objects
        for mo in math_objects:
            self.addItem(mo)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # Init context menu
        isav = lambda x: True
        isnotav = lambda x: False
        actions = [ContextMenuAction('My first action', isav),
                   ContextMenuAction('Oh yeah I love action', isav),
                   ContextMenuAction('This one is not enabled', isnotav),
                   ContextMenuAction('Wait this one too?', isnotav),
                   ContextMenuAction('Fucking finally this one is', isav)]
        context_menu = ContextMenu(actions)
        self.context_menu = context_menu

    def current_selection(self):
        l = []
        for mo in self.math_objects:
            if mo.isSelected():
                l.append(mo)
        return l

    def contextMenuEvent(self, event):
        self.context_menu.set_availability(self.current_selection)
        self.context_menu.exec_(self.mapToGlobal(event.pos()))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        math_objects = [MathObject('Pink Floyd'),
                        MathObject('Genesis'),
                        MathObject('Year of no light')]
        math_object_widget = MathObjectWidget(math_objects)
        self.setCentralWidget(math_object_widget)


if __name__ == '__main__':
    app = QApplication()
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
