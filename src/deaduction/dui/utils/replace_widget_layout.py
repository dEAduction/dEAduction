"""
#####################################################################
# replace_widget_layout.py : Provide replace_widget_layout function #
#####################################################################

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

from PySide2.QtCore    import   Qt
from PySide2.QtWidgets import ( QLayout,
                                QWidget)


def replace_widget_layout(layout: QLayout, old: QWidget, new: QWidget,
                          recursive: bool = True):
    """
    Replace an old widget by a new one in a layout.

    :param layout: The layout in which we replace the widget.
    :param old: The old / replaced widget.
    :param new: The new / replacing widget.
    :param recursive: If recursive is True, the function looks for old
        in layout's sub-layouts.
    """

    flag = Qt.FindChildrenRecursively if recursive else \
            ~Qt.FindChildrenRecursively
    layout.replaceWidget(old, new, flag)
    old.deleteLater()
