"""
#####################################################
# classes.py : Utilitary classes for deaduction.dui #
#####################################################

Author(s)      : Kryzar <antoine@hugounet.com>
Maintainers(s) : Kryzar <antoine@hugounet.com>
Date           : October 2020

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

from typing import Dict

from PySide2.QtCore    import   Qt
from PySide2.QtWidgets import ( QTreeWidget,
                                QTreeWidgetItem)

# TODO: Comment me

class DisclosureTree(QTreeWidget):
    # An implementation of a disclosure triangle.
    # https://stackoverflow.com/questions/63862724/
    # qtreeview-dynamic-height-according-to-content-disclosure-triangle

    def __init__(self, title: str, data: Dict[str, str]):

        super().__init__()

        # ─────────────────── Add content ────────────────── #

        self.setColumnCount(2)
        parent_item = QTreeWidgetItem(self, [f'{title} : '])
        parent_item.set_selectable(False)
        self.addTopLevelItem(parent_item)

        for key, val in data.items():
            item = QTreeWidgetItem(parent_item, [f'{key} : ', val])
            parent_item.addChild(item)

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
        hint.setHeight(self.get_height() + self.frameWidth() * 2)
        return hint

    def minimumSizeHint(self):
        return self.sizeHint()
