"""
calculator_targets.py : provide the CalculatorTargets class.

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 12 2023
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2023 the d∃∀duction team

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


from PySide2.QtCore import Signal, Slot, Qt, QTimer, QSettings
from PySide2.QtGui     import  QKeySequence, QIcon
from PySide2.QtWidgets import (QTextEdit, QWidget,
                               QSizePolicy, QScrollArea,
                               QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QToolBar,
                               QAction, QDialog, QDialogButtonBox,
                               QCheckBox,
                               QGroupBox)


from deaduction.dui.primitives.base_math_widgets_styling import MathTextWidget
from deaduction.dui.stages.calculator.calculator_button import CalculatorButton


class CalculatorTarget(MathTextWidget):
    """
    This is the class for the Calculator "target", whose purpose is to
    display the MathObject (or more precisely, MarkedPatternMathObject) that
    usr is building. Note that the text from kbd is not processed by the
    super class QTextEdit, unless Calculator is in Lean mode. Instead,
    kbd events are intercepted and serve as shorcuts from buttons. All input
    come from the buttons.
    """
    def __init__(self):
        super().__init__()
        self.set_highlight(True)

        self.setFixedHeight(50)  # fixme
        # self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.NoWrap)
        # self.setLineWrapColumnOrWidth(10000)

        self.key_event_buffer = ""
        self.navigation_bar = None
        self.toolbar = None
        self.button_box = None

        self.key_buffer_timer = QTimer()
        self.key_buffer_timer.setSingleShot(True)
        self.key_buffer_timer.timeout.connect(self.key_buffer_timeout)

        self.lean_mode = False  # TODO: change behavior in Lean mode
        self.check_types = False  # TODO: add button?

    def mousePressEvent(self, event):
        if self.lean_mode:
            super().mousePressEvent(event)
        else:
            self.setFocus()
            event.ignore()

    def mouseDoubleClickEvent(self, event):
        if self.lean_mode:
            super().mouseDoubleClickEvent(event)
        else:
            self.setFocus()
            event.ignore()

    def keyPressEvent(self, event):
        """
        Take focus (from calculator_target) so that shortcuts to buttons
        work.
        """

        if self.lean_mode:
            super().keyPressEvent(event)
            return

        self.key_buffer_timer.setInterval(1000)
        self.key_buffer_timer.start()

        key = event.key()
        # print(f"Key: {key}")
        # print(f"Event: {event}")
        if event.modifiers() & Qt.ControlModifier:
            key += Qt.CTRL
            # print(key_sqc)
            # print(key_sqc == QKeySequence.Undo)
        if event.modifiers() & Qt.ShiftModifier:
            key += Qt.SHIFT
        if event.modifiers() & Qt.AltModifier:
            key += Qt.ALT
        if event.modifiers() & Qt.MetaModifier:
            key += Qt.META

        key_sequence = QKeySequence(key)
        # print(key_sequence == QKeySequence.Undo)
        if key_sequence == QKeySequence("Return"):
            self.button_box.button(QDialogButtonBox.Ok).animateClick()
        elif key_sequence == QKeySequence("Space"):
            self.key_buffer_timer.stop()
            self.key_buffer_timeout()

        # QAction key sequences
        action = None
        bar = None
        # Navigation
        if key_sequence == QKeySequence.MoveToPreviousWord:
            bar = self.navigation_bar
            action = bar.beginning_action
        elif key_sequence == QKeySequence.MoveToPreviousChar:
            bar = self.navigation_bar
            action = bar.left_action
        elif key_sequence == QKeySequence.MoveToNextChar:
            bar = self.navigation_bar
            action = bar.right_action
        elif key_sequence == QKeySequence.MoveToNextWord:
            bar = self.navigation_bar
            action = bar.end_action
        elif key_sequence == QKeySequence.MoveToPreviousLine:
            bar = self.navigation_bar
            action = bar.up_action
        elif key_sequence == QKeySequence.Delete:
            bar = self.navigation_bar
            action = bar.delete
        elif key_sequence == QKeySequence.NextChild:
            bar = self.navigation_bar
            action = bar.right_unassigned_action

        # Main toolbar
        elif key_sequence == QKeySequence.Undo:
            bar = self.toolbar
            action = bar.undo_action
        elif key_sequence == QKeySequence.Redo:
            bar = self.toolbar
            action = bar.redo_action

        if bar and action:
            bar.animate_click(action)
            self.clear_key_buffer()
            event.ignore()
            return

        # Text shortcuts
        text = event.text()
        if text:
            self.key_event_buffer += text
            # print(self.key_event_buffer, self.key_buffer_timer)
            yes = CalculatorButton.process_key_events(self.key_event_buffer,
                                                      timeout=False)
            if yes:
                self.clear_key_buffer()

        event.ignore()

    @Slot()
    def key_buffer_timeout(self):
        CalculatorButton.process_key_events(self.key_event_buffer,
                                            timeout=True)
        self.key_event_buffer = ""

    def clear_key_buffer(self):
        self.key_event_buffer = ""
        self.key_buffer_timer.stop()

    def go_to_position(self, new_position):
        cursor = self.textCursor()

        if new_position == -1:
            self.moveCursor(cursor.End, cursor.MoveAnchor)
        else:
            old_position = cursor.position()
            cursor.movePosition(cursor.NextCharacter,
                                cursor.MoveAnchor,
                                new_position - old_position)
            self.setTextCursor(cursor)


class CalculatorTargets(QWidget):
    """
    This class displays one or several CalculatorTarget,
    with a common detailed context and individual titles.
    It also displays a toolbar with history moves, and a navigation bar.
    """


