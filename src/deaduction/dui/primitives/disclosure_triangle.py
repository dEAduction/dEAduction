"""
# disclosure_triangle.py: a QToolButton to show/hide a widget. #


Author(s)     : F Le Roux
Maintainer(s) : F. Le Roux
Created       : 04 2022 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the dEAduction team

This file is part of dEAduction.

    dEAduction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    dEAduction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""

from PySide2.QtWidgets import (QSizePolicy, QToolButton)
from PySide2.QtCore import Qt, Slot


class DisclosureTriangle(QToolButton):
    """
    A QToolButton that changes appearance and call a function when clicked.
    """

    def __init__(self, slot: callable, hidden=False):
        super().__init__()
        self.slot = slot
        # self.setText("▷" if hidden else "▽")
        self.hidden = hidden
        self.setArrowType(Qt.RightArrow if hidden else Qt.DownArrow)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.clicked.connect(self.toggle)

    @Slot()
    def toggle(self):
        """
        Modify self's appearance and call the slot function.
        """
        self.hidden = not self.hidden
        self.setArrowType(Qt.RightArrow if self.hidden else Qt.DownArrow)
        self.slot()

