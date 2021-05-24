"""
#############################################################
# menu_outline.py : Provide menu outline type and functions #
#############################################################

    Provide type alias MenuOutlineType and function
    create_menu_recursively. Menus have a structure that looks like
    this:

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
        — the `List` is composed of actions (`MenuBarAction`) and
        submenus (`Tuple`).
    In the above example, Menu2 would be:
    Menu2 = ('Menu2', [Action21,
                       Action22,
                       ('SubSubMenu21', [Action211])])
    See snippets/menubar for a full (but crappy) example.

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
                    Tuple,
                    Union)

from PySide2.QtWidgets import (QAction,
                               QMenu)

MenuOutlineType = List[Union[QAction, Tuple[str, List]]]

def create_menu_recursively(current: QMenu, children: MenuOutlineType):
    """
    Given a menu outline, properly instanciate a QMenu from a given
    outline. This function is recursive so the initial call should
    probably look like:
    create_menu_recursively(my_menu, my_outline)

    This function first goes through each menu in self (a List). It sees
    that no element in this list is an action (tested with
    `isinstance(child, Action)`).  Therefore all those items are menus,
    and the function calls itself on this menus. This goes on until the
    function find some element in some menu which is an action. At this
    point, all the hierarchy for *this* action has been set up and the
    function adds the action and returns. All paths are independent.
    """
    for child in children:
        if isinstance(child, QAction):
            current.addAction(child)
        else:  # child is of type List[Union[…
            title, childrenchildren = child
            menu = MenuBarMenu(parent_qmw, title)
            current.addMenu(menu)
            create_menu_recursively(menu, childrenchildren)
