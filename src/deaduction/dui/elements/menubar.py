"""
######################################
# menubar.py : Provide menubar stuff #
######################################

    Provide following classes:
    — MenuBar,
    — MenuBarAction,
    — MenuBarMenu.

Author(s)      : Kryzar <hg4fpchw@anonaddy.me>
Maintainers(s) : Kryzar <hg4fpchw@anonaddy.me>
Date           : May 2021

Copyright (c) 2021 the dEAduction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    d∃∀duction is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with d∃∀duction. If not, see <https://www.gnu.org/licenses/>.
"""
from typing import (List,
                    Optional,
                    Union,
                    Tuple)

from PySide2.QtWidgets import (QAction,
                               QMainWindow,
                               QMenu,
                               QMenuBar)

from .menu_outline import (create_menu_recursively,
                           MenuOutlineType)

# ┌─────────┐
# │ MenuBar │
# └─────────┘


class MenuBar(QMenuBar):
    """
    Menubar for dEAduction's main windows (especially
    ExerciseMainWindow). This class does not do much besides inheriting
    QMenuBar. Its operation is simple: one gives MenuBar.__init__ an
    outline of the menu (see MenuBar.__init__ docstring) and it is
    set-up.
    """
    def __init__(self, parent_qmw: QMainWindow, outline: MenuOutlineType):
        """
        So, to set use this class,
        1. go to its parent instance QMainWindow,
        2. crate menus and actions beforehand,
        3. connect actions to their slots,
        4. put all this in an outline (outline = [('Menu 1…),
        5. init this class,
        6. set this instance as the main window's menu bar with the method
        QMainWindow.setMenuBar.

        :param parent_qmw: The instance of QMainWindow which is parent
                           to this menubar. This is required because Qt
                           is full of shit.
        :param outline: Outline of the menu to be set-up.
        """
        super().__init__()
        create_menu_recursively(self, outline)


# ┌───────────────────────────────────┐
# │ Items: MenuBarAction, MenuBarMenu │
# └───────────────────────────────────┘


class MenuBarAction(QAction):
    """
    QAction class for MenuBar. This class does nothing more than QAction
    except setting up the action's title and tooltip at init.

    It would have been nice to give this class a slot (e.g. called fn)
    at init, so that all the boiler-code
    ```
    self.triggered.connect(fn)
    ```
    would be hidden in the definition of the class. I (Kryzar) did not
    do this because there are multiple possible signals
    (`QAction.triggered`, `QAction.toggled`) that have a very different
    behavior to `QAction.triggered`. It seems reasonable to wait and see
    how we use ExerciseMainWindow's menubar and write good code after.
    """
    def __init__(self, parent_qmw: QMainWindow,
                 title: str, tooltip: Optional[str] = None):
        """
        Init self with a title and a tooltip. Do not forget parent_qmw!

        :param parent_qmw: The instance of QMainWindow which is parent
                           to this menubar. This is required because Qt
                           is full of shit.
        :param title: Title of the action.
        :param tooltip: Tooltip of the action.
        """
        super().__init__(parent_qmw)
        self.setText(title)
        if tooltip:
            self.setToolTip(tooltip)


class MenuBarMenu(QMenu):
    """
    QMenu action for MenuBar. This class sets up the menu's title. Tbh,
    this class is useless, as it does nothing more than QMenu and
    QMenu.__init__ do themselves. However, having it makes the code
    cleaner in other parts of the project.
    """
    def __init__(self, parent_qmw: QMainWindow,
                 title: str):
        """
        Init self with a title. Do not forget parent_qmw!

        :param parent_qmw: The instance of QMainWindow which is parent
                           to this menubar. This is required because Qt
                           is full of shit.
        :param title: Title of the action.
        """
        super().__init__(parent_qmw)
        self.setTitle(title)
