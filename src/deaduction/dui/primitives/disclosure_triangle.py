"""
# disclosure_triangle.py: provide DisclosureTriangles Classes #


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

from PySide2.QtWidgets import (QSizePolicy, QToolButton, QLabel)
from PySide2.QtCore import Qt, Slot, Signal


class DisclosureTriangle(QToolButton):
    """
    A QToolButton that changes appearance and call a function when clicked.
    """

    hidden_triangle = "▷"
    shown_triangle = "▽"

    def __init__(self, slot: callable, hidden=False):
        super().__init__()
        self.setStyleSheet("font-weight: bold;")
        self.slot = slot
        # self.setText("▷" if hidden else "▽")
        self.hidden = hidden
        self.setText(self.hidden_triangle if hidden else self.shown_triangle)
        # self.setArrowType(Qt.RightArrow if hidden else Qt.DownArrow)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.clicked.connect(self.toggle)

    @Slot()
    def toggle(self):
        """
        Modify self's appearance and call the slot function.
        """
        self.hidden = not self.hidden
        self.setText(self.hidden_triangle if self.hidden
                     else self.shown_triangle)
        self.slot()


class DisclosureTitleWidget(QLabel):
    """
    A QLabel with a disclosure triangle integrated in the text; click emit
    the 'clicked' signal.
    """
    hidden_triangle = "<b>▷ </b>"
    shown_triangle = "<b>▽ </b>"
    # ► ▼

    clicked = Signal()

    def __init__(self, title, hidden=False):
        super().__init__()
        # self.setFocusPolicy(Qt.NoFocus)
        self.title = title
        self.hidden = hidden
        self.set_text()

    def set_text(self):
        title = '<b>' + self.title + '</b>'
        text = (self.hidden_triangle + title if self.hidden
                else self.shown_triangle + title)
        self.setText(text)

    def set_hidden(self, hidden=None):
        if hidden is None:
            self.hidden = not self.hidden
        else:
            self.hidden = hidden
        self.set_text()

    def mousePressEvent(self, event):
        self.clicked.emit()




