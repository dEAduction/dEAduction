# A menubar for a QMainWindow

import logging
import sys
from typing import (Callable,
                    List,
                    Union,
                    Tuple)

from PySide2.QtWidgets import (QApplication,
                               QMainWindow,
                               QAction,
                               QMenu,
                               QMenuBar,
                               QPushButton,
                               QLabel)

from deaduction.pylib import logger

logger.configure()
log = logging.getLogger()

# ┌───────┐
# │ Items │
# └───────┘


class MenuBarAction(QAction):
    def __init__(self, parent_qmw: QMainWindow, name: str, slot: Callable):
        super().__init__(parent_qmw)
        self.setText(name)


class MenuBarMenu(QMenu):
    def __init__(self, parent_qmw: QMainWindow, name: str):
        super().__init__(parent_qmw)
        self.setTitle(name)


# ┌─────────┐
# │ Menubar │
# └─────────┘


class AbstractMenuBar(QMenuBar):
    def __init__(self, parent_qmw: QMainWindow, outline: List[Tuple[str, List]]):
        super().__init__(parent_qmw)

        # Add menus and actions

        def recursive(current: QMenu,
                      children: List[Union[QAction, Tuple[str, List]]]):
            for child in children:
                if isinstance(child, QAction):
                    current.addAction(child)
                else:  # child is of type List[Union[…
                    title, childrenchildren = child
                    menu = MenuBarMenu(parent_qmw, title)
                    current.addMenu(menu)
                    recursive(menu, childrenchildren)
        recursive(self, outline)

# ┌─────────────┐
# │ Main window │
# └─────────────┘


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        def foo(): pass
        outline = [('Exercise', [('Go to…', [MenuBarAction(self, 'Next exercise', foo),
                                              MenuBarAction(self, 'Launcher', foo)]),
                                  ('Actions', [MenuBarAction(self, 'Undo', foo),
                                               MenuBarAction(self, 'Start again', foo)]),
                                   MenuBarAction(self, 'Toggle LEAN mode', foo)]),
                    ('LEAN', [('Code', [MenuBarAction(self, 'Show console', foo)])]),
                     ('Contribute', [MenuBarAction(self, 'Diamong hands', foo)])]
        menubar = AbstractMenuBar(self, outline)
        self.setMenuBar(menubar)


if __name__ == '__main__':
    app = QApplication()
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
