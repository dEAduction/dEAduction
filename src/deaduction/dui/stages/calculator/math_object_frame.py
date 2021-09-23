"""
# math_object_widget.py : display MathObject (and PatternMathObject)
 in nested widgets that reflects the tree-like structure #
    
    <#optionalLongDescription>

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 09 2021 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the d∃∀duction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    d∃∀duction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import logging

from PySide2.QtCore import (    Signal,
                                Slot,
                                Qt)

from PySide2.QtWidgets import ( QApplication,
                                QWidget,
                                QFrame,
                                QLabel,
                                QVBoxLayout,
                                QHBoxLayout,
                                QPushButton,
                                QSizePolicy,
                                QAction
                                )

from deaduction.pylib.mathobj import MathObject, Shape, latex_to_utf8

global _


def _(s):
    return s


class ElementaryStringWidget(QLabel):
    def __init__(self, math_to_display):
        to_display = latex_to_utf8(math_to_display)
        super().__init__(to_display)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)


class ElementaryButtonWidget(QPushButton):
    def __init__(self, math_object):
        to_display = latex_to_utf8(math_object.to_display())
        super().__init__(text=to_display)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setCheckable(True)


class MathObjectFrame(QFrame):

    def __init__(self, math_object: MathObject):
        super().__init__()
        layout = QHBoxLayout()

        self.children_widgets = []
        # Case of APPLICATION
        math_children = ([math_object.implicit_children(n) for n in
                          range(math_object.nb_implicit_children())]
                         if math_object.is_application()
                         else math_object.children)
        # format_ = "utf-8"
        shape = Shape.raw_shape_from_math_object(math_object)
        display = shape.display

        for item in display:
            if isinstance(item, str):
                child_widget = ElementaryStringWidget(item)
            elif isinstance(item, int):
                math_child = math_children[item]
                if math_child.children:
                    child_widget = MathObjectFrame(math_children[item])
                else:
                    child_widget = ElementaryButtonWidget(math_child)
            elif len(item) == 1:
                child_widget = MathObjectFrame(item[0])
            else:
                child_widget = MathObjectFrame(item)

            self.children_widgets.append(child_widget)

        for child_widget in self.children_widgets:
            layout.addWidget(child_widget)

        # Cosmetic
        layout.setSpacing(0)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Sunken)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.setLayout(layout)

        # Events
        self.setFocusPolicy(Qt.StrongFocus)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # window = MathObjectWidget()

    # window.show()
    # sys.exit(app.exec_())

