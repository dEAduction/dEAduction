"""
##################################
# menus.py : Provide menus stuff #
##################################

    Provide following classes:
    - Menu,
    - MenuAction,
    — MenuBar,
    and type alias MenuOutlineType.

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
from typing import (Any,
                    Callable,
                    List,
                    Optional,
                    Union,
                    Tuple)

from PySide2.QtWidgets import (QAction,
                               QMenu,
                               QMenuBar,
                               QWidget)

# Avoid circular import
from .context_widgets_classes import (MathObject,
                                      MathObjectWidget)

# ┌──────────────┐
# │ Menu outline │
# └──────────────┘

MenuOutlineType = List[Union[QAction, Tuple[str, List]]]
"""
Menus have a structure that looks like this:

Instance of QMenu (or QMenuBar)
├── Menu1
│   ├── SubMenu1
│   └── SubMenu2
│       ├── Action121
│       ├── Action122
│       └── SubSubMenu121
│           └── Action1211
├── Menu2
│   ├── Action21
│   ├── Action22
│   └── SubMenu21
│       └── Action211
└── Menu3
    └── Action31

Each menu (any sub…menu is considered a menu) is represented by
Tuple[str, List[Union[MenuBarAction, Tuple]]]]:
    — the `str` is the title of the menu,
    — the `List` is composed of actions (`MenuBarAction`) and submenus
    (`Tuple`).
In the above example, Menu2 would be:
Menu2 = ('Menu2', [Action21,
                   Action22,
                   ('SubSubMenu21', [Action211])])
See snippets/menubar for a full (but crappy) example.
"""


def create_menu_recursively(parent: QWidget, current: QMenu,
                            children: MenuOutlineType) -> [QAction]:
    """
    Given a menu outline, properly instanciate a QMenu from a given
    outline. Furthermore, return the list of actions of the menu
    (tree structure is lost, useful to enable/disable actions depending
    on the current context).

    This function is recursive so the initial call should probably look
    like:
    ```
    create_menu_recursively(parent_wgt, my_menu, my_outline)
    ```
    This function first goes through each menu in self (a List). It sees
    that no element in this list is an action (tested with
    `isinstance(child, Action)`).  Therefore all those items are menus,
    and the function calls itself on this menus. This goes on until the
    function find some element in some menu which is an action. At this
    point, all the hierarchy for *this* action has been set up and the
    function adds the action and returns. All paths are independent.

    :param parent: The parent widget, e.g. the parent QMainWindow.
    :param current: Current menu on which the function is called. At
                    initial call, this should be ```my_menu``` (self
                    most of the time).
    :param children: Menu outline of current.
    :return: List (not tree) of MenuAction's of the menu.
    """
    for child in children:
        if isinstance(child, QAction):
            current.addAction(child)
        else:  # child is of type List[Union[…
            title, childrenchildren = child
            menu = Menu(parent, title)
            current.addMenu(menu)
            create_menu_recursively(menu, childrenchildren)

# ┌───────────────────┐
# │ Menus and actions │
# └───────────────────┘


class Menu(QMenu):
    """
    QMenu action for MenuBar. This class sets up the menu's title. aving
    it makes the code cleaner in other parts of the project.
    """
    def __init__(self, parent: QWidget, title: str):
        """
        Init self with a title. Do not forget parent_!

        :param parent: The parent widget, e.g. the parent QMainWindow.
        :param title: Title of the action.
        """
        super().__init__(parent)
        self.setTitle(title)


class MenuAction(QAction):
    """
    QAction class for MenuBar, context menus, etc. This class does
    nothing more than QAction except setting up the action's title and
    tooltip at init.

    It would have been nice to give this class a slot (called fn here)
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
    def __init__(self, parent: QWidget, title: str,
                 tooltip: Optional[str] = None,
                 enable: Optional[Callable[Any, bool]] = None):
        """
        Init self. Don't forget parent!

        :param parent: The parent widget, e.g. the parent QMainWindow.
        :param title: Title of the action.
        :param tooltip: Tooltip of the action.
        :param enable: Function (with or w/o arguments) to be called in
                       the parent menu (e.g. MOWContextMenu) to determine
                       whether or not self is to be enabled or not
                       depending on the current context.
        """
        super().__init__(parent)
        self.setText(title)
        if tooltip:
            self.setToolTip(tooltip)
        if enable:
            self.__enable = enable

    @property
    def enable(self) -> Optional[Callable]:
        """
        A reference to self.__enable, if it exists, which accepts
        arguments.
        """
        if self.__enable:
            return self.__enable
        else:
            return None


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
    def __init__(self, outline: MenuOutlineType):
        """
        So, to set use this class,
        1. go to its parent instance QMainWindow,
        2. crate menus and actions beforehand,
        3. connect actions to their slots,
        4. put all this in an outline (outline = [('Menu 1…),
        5. init this class,
        6. set this instance as the main window's menu bar with the method
        QMainWindow.setMenuBar.

        :param outline: Outline of the menu to be set-up.
        """
        super().__init__()
        create_menu_recursively(self, self, outline)


# ┌───────────────────────────────┐
# │ MathObjectWidget context menu │
# └───────────────────────────────┘


class MOWContextMenu(QMenu):
    """
    Context menu for MathObjectWidget.
    """
    def __init__(self, parent_MOW: MathObjectWidget,
                 outline: MenuOutlineType):
        """
        Init self with a menu outline.

        :parent_MOW: Parent MathObjectWidget.
        :param outline: Menu outline.
        """
        super().__init__()
        self.__actions = create_menu_recursively(parent_MOW, self, outline)

    def enable_actions(self, current_selection: [MathObject]):
        """
        Enable or disable actions depending on the current selection.

        :param current_selection: Current context selection.
        """
        for action in self.__actions:
            if action.is_available:
                action.setEnabled(action.is_available(current_selection))
            else:
                action.setEnabled(True)
