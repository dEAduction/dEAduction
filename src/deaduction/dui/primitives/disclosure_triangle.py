"""
#############################################################
# disclosure_triangle.py : Provide DisclosureTriangle class #
#############################################################

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

from typing import Dict

from PySide2.QtCore    import   Qt
from PySide2.QtWidgets import ( QTreeWidget,
                                QTreeWidgetItem)

from deaduction.dui.utils import set_selectable


class DisclosureTriangle(QTreeWidget):
    """
    An (very basic) implementation of a DisclosureTriangle, i.e. a
    widget that looks like this:

    ____________________
    |                  |
    |  |> Title:       |
    |      key1: val1  |
    |      key2: val2  |
    |      …           |
    --------------------

    This triangle can be expanded or collapsed and is instanciated with
    a title and a dictionnary of keys and values. Made with the help of
    musicamente on Stackoverflow:  https://stackoverflow.com/questions/
    63862724/
    qtreeview-dynamic-height-according-to-content-disclosure-triangle.
    """

    def __init__(self, title: str, data: Dict[str, str]):
        """
        Init self with a title and a dictionnary of keys and values (see
        self docstring).

        :param title: The title of the disclosure tree (e.g. 'Details'
            in dEAduction's course and exercise choosers.
        :param data: The data to be displayed in the disclosure
            triangle.
        """

        super().__init__()

        # ─────────────────── Add content ────────────────── #

        self.setColumnCount(2)
        self.__parent_item = QTreeWidgetItem(self, [f'{title} : '])
        self.__parent_item.set_selectable(False)
        self.addTopLevelItem(self.__parent_item)

        for key, val in data.items():
            item = QTreeWidgetItem(self.__parent_item, [f'{key} : ', val])
            self.__parent_item.addChild(item)

            # Cosmetics
            item.set_selectable(False)
            item.setTextAlignment(0, Qt.AlignRight)

        # ──────────────────── Cosmetics ─────────────────── #

        # Hide header
        self.header().hide()

        # No background
        self.setStyleSheet('background-color: transparent;')

        # Dynamically change height when widget is collapsed or expanded
        # You have to update the maximum height of the widget, based on
        # its contents. For each top item you need to get the height for
        # that row using rowHeight() and do the same recursively for
        # child items whenever the item is expanded. Also, you need to
        # overwrite the sizeHint and minimumSizeHint.
        self.expanded.connect(self.update_height)
        self.collapsed.connect(self.update_height)

    def expand(self, yes: bool = True):
        """
        Expand the tree is yes is True, collapse it otherwise.

        :param yes: See above.
        """

        if yes:
            self.expandItem(self.__parent_item)
        else:
            self.collapseItem(self.__parent_item)

    #####################
    # Redifined methods #
    #####################

    # See
    # https://stackoverflow.com/questions/63862724/
    # qtreeview-dynamic-height-according-to-content-disclosure-triangle

    def update_height(self):
        self.setMaximumHeight(self.sizeHint().height())

    def get_height(self, parent=None):
        height = 0
        if not parent:
            parent = self.rootIndex()
        for row in range(self.model().rowCount(parent)):
            child = self.model().index(row, 0, parent)
            height += self.rowHeight(child)
            if self.isExpanded(child) and self.model().hasChildren(child):
                height += self.get_height(child)
        return height

    def sizeHint(self):
        hint = super().sizeHint()
        # The + 10 avoids an ugly scroll bar
        hint.setHeight(self.get_height() + 10 + self.frameWidth() * 2)
        return hint

    def minimumSizeHint(self):
        return self.sizeHint()
