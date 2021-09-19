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
                                Slot)
from PySide2.QtWidgets import ( QApplication,
                                QWidget,
                                QFrame,
                                QLabel,
                                QVBoxLayout,
                                QHBoxLayout,
                                QPushButton,
                                QSizePolicy)

from deaduction.pylib.mathobj import MathObject, Shape

global _


def _(s):
    return s


class ElementaryMathWidget(QLabel):
    def __init__(self, math_to_display, format_="utf-8"):
        # if format_ is "uft-8":
        super().__init__(math_to_display)
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Sunken)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)


class MathListStringWidget(QFrame):
    def __init__(self, display: [], format_='utf-8'):
        self.children = []
        for child in display:
            if isinstance(child, str):
                child_widget = ElementaryMathWidget(child, format_)
            elif len(child) == 1:
                child_widget = ElementaryMathWidget(child[0], format_)
            else:
                child_widget = MathListStringWidget(child)

            self.children.append(child_widget)

        super().__init__()
        layout = QHBoxLayout()
        for child_widget in self.children:
            layout.addWidget(child_widget)

        # Cosmetic
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Sunken)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.setLayout(layout)


class MathObjectWidget(QWidget):

    def __init__(self, math_object: MathObject):
        super().__init__()

        shape = Shape.from_math_object(math_object)
        layout = QVBoxLayout()
        layout.addWidget(MathListStringWidget(shape.display))

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # window = MathObjectWidget()
    display = ["∀", "x", "∈", "X", " ,", [["f", "(", "x", ")"], " = ", "x"]]
    display2 = ['∀', ['x'], ' ∈ ', ['X'], ', ', ['∀', ["x'"], ' ∈ ', ['X'], ', ', ['(', [[['g'], '∘', ['f'], '(', ['x'], ')'], ' = ', [['g'], '∘', ['f'], '(', ["x'"], ')']], ' ⇒ ', [['x'], ' = ', ["x'"]], ')']]]
    display_limit1 = [['(', ['lim', ['(', 'u', ['_', 'n'], ')', ['_', 'n'], ' ∈ ', 'ℕ'], ' = ', ['l']], ' and ', ['lim', ['(', 'u', ['_', 'n'], ')', ['_', 'n'], ' ∈ ', 'ℕ'], ' = ', ["l'"]], ')'], ' ⇒ ', [['l'], ' = ', ["l'"]]]
    display_limit2 = ['∀', [['ε'], ' > ', ['0']], ', ', ['∃', ['n'], ' ∈ ', ['ℕ'], ', ', ['(', ['(', ['n'], ' > ', ['0'], ')'], ' and ', ['(', '∀', [["n'"], ' ≥ ', ['n']], ', ', [['|', [['u', ['_', ["n'"]]], ' - ', ['l']], '|'], ' < ', ['ε']], ')'], ')']]]
    window = MathListStringWidget(display_limit2)
    window.show()
    sys.exit(app.exec_())

