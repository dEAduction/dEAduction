"""
#######################################################
# set_selectable.py : Provide set_selectable function #
#######################################################

Author(s)      : Kryzar <antoine@hugounet.com>
Maintainers(s) : Kryzar <antoine@hugounet.com>
Date           : January 2021

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

# FIXME: the whole file is obsolete
from PySide2.QtWidgets import QTreeWidgetItem
from PySide2.QtCore    import Qt
# from sys               import version_info


def set_selectable(self: QTreeWidgetItem, yes: bool = True):
    """
    This method is made for QTreeWidgetItem but probably works for other
    items as well. Make self to be selectable if yes or unselectable
    otherwise.  There is no built-in method for this so we use flags as
    if we are in 1980 (thanks Florian).

    :param yes: See above.
    """

    if yes:
        self.setFlags(int(Qt.ItemIsEnabled) | int(Qt.ItemIsSelectable))
    else:
        self.setFlags(Qt.ItemIsEnabled)


QTreeWidgetItem.set_selectable = set_selectable
