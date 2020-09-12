"""
######################################
# functions.py : utilities functions #
######################################

Author(s)      : Kryzar <antoine@hugounet.com>
Maintainers(s) : Kryzar <antoine@hugounet.com>
Date           : July 2020

Copyright (c) 2020 the dEAduction team

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

from PySide2.QtCore    import   Qt
from PySide2.QtWidgets import ( QLayout,
                                QTreeWidgetItem,
                                QWidget)


def replace_delete_widget(layout: QLayout, old: QWidget, new: QWidget,
                          flag=Qt.FindChildrenRecursively):
    layout.replaceWidget(old, new, flag)
    old.deleteLater()
    
def set_selectable(self, yes: bool=True):
    """
    Make self to be selectable if yes or unselectable otherwise.
    There is no built-in method for this so we use flags as if we
    are in 1980 (thanks Florian).

    :param yes: See above.
    """

    if yes:
        new_flags = self.flags() &  Qt.ItemIsSelectable
    else:
        new_flags = self.flags() & ~Qt.ItemIsSelectable
    self.setFlags(new_flags)

QTreeWidgetItem.set_selectable = set_selectable
