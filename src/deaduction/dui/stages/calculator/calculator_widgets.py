"""
# calculator_widgets.py : widgets for calculator #
    


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

from PySide2.QtCore import Signal, Slot

from PySide2.QtWidgets import ( QApplication,
                                QWidget,
                                QFrame,
                                QLabel,
                                QVBoxLayout,
                                QHBoxLayout,
                                QPushButton,
                                QSizePolicy,
                                QAction)

from deaduction.pylib.mathobj import MathObject, Goal
from deaduction.pylib.coursedata import Exercise

from .math_object_frame import MathObjectFrame


class CalculatorButton(QPushButton):
    def __init__(self, math_object):
        self.math_object = math_object
        display = math_object.to_display()
        super().__init__(text=display)


class PatternButtonsWidget(QFrame):
    """
    A class for displaying a list of math_objects as buttons.
    The buttons allow the user to add the math_object in a calculator.
    """
    def __init__(self, math_objects: [MathObject], title: str):

        super().__init__()
        self.setWindowTitle(title)
        layout = QHBoxLayout()
        layout.setSpacing(1)

        # Buttons
        self.buttons = []
        for math_object in math_objects:
            button = CalculatorButton(math_object)
            self.buttons.append(button)
            layout.addWidget(button)

        self.setLayout(layout)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Sunken)


class CalculatorButtonsWidget(QWidget):
    """A class for displaying several rows of buttons for the calculator.
    Each row is an instance of PatternButtonsWidget, with a title."""
    def __init__(self, elements: (str, [[MathObject]]) ):
        """

        :param elements:
        """
        super().__init__()
        layout = QVBoxLayout()

        self.rows = []
        for title, math_objects in elements:
            row = PatternButtonsWidget(math_objects, title)
            self.rows.append(row)
            
            layout.addWidget(row)
            
        self.setLayout(layout)
            

class Calculator(QWidget):
    button_pressed = Signal(MathObject)

    def __init__(self, exercise, goal, parent=None):
        """
        A "calculator" for the user to create new math objects.
        """
        super().__init__(parent=parent)
        layout = QVBoxLayout()

        # Buttons
        elements = pattern_math_objects_from_goal_and_exercise(exercise, goal)
        
        calculator_buttons = CalculatorButtonsWidget(elements)
        layout.addWidget(calculator_buttons)
        
        # Screen
        nothing = MathObject(node="MESSAGE",
                             info={'name': _("Click to build some object")},
                             children=[])
        
        screen = MathObjectFrame(nothing)
        layout.addWidget(screen)
        
        self.setLayout(layout)

    @Slot()
    def display_math_object(self, math_object):
        """
        Display math_Object on the calculator's screen.
        """
        # TODO
        pass

    @Slot()
    def toggle(self):
        self.setVisible(not self.isVisible())


def pattern_math_objects_from_goal_and_exercise(exercise, goal):
    """
    Construct elements for the CalculatorButtonsWidget Widget from exercise
    and goal.
    """
    # TODO
    elements = []

    # Context
    context = (_("Context"), goal.context_objects)
    elements.append(context)

    # Definitions

    return elements

