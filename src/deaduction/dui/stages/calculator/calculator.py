"""
calculator.py : provide the Calculator and CalculatorWindow class.

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 06 2023 (creation)
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

if __name__ == '__main__':
    from deaduction.dui.__main__ import language_check

    language_check()

import sys
import logging
from typing import Union, List

from PySide2.QtCore import Signal, Slot, Qt, QCoreApplication
from PySide2.QtGui     import  QKeySequence, QIcon, QTextDocument
from PySide2.QtWidgets import (QApplication, QTextEdit, QToolButton, QWidget,
                               QHBoxLayout, QVBoxLayout, QLabel, QToolBar,
                               QAction, QDialog, QDialogButtonBox,
                               QShortcut)

import deaduction.pylib.config.vars as cvars
import deaduction.pylib.config.dirs as cdirs
import deaduction.pylib.utils.filesystem as fs

from deaduction.pylib.math_display import MathDisplay

from deaduction.pylib.pattern_math_obj import (PatternMathObject,
                                               MarkedPatternMathObject,
                                               MarkedMetavar,
                                               CalculatorPatternLines,
                                               calculator_group,
                                               sci_calc_group,
                                               logic_group,
                                               set_theory_group)

from deaduction.dui.elements import TargetLabel
from deaduction.dui.primitives.base_math_widgets_styling import MathTextWidget

global _
log = logging.getLogger(__name__)

if __name__ == "__main__":
    from deaduction.pylib import logger
    logger.configure(domains="deaduction",
                     display_level="debug",
                     filename=None)


class CalculatorTarget(MathTextWidget):

    def __init__(self):
        super().__init__()
        self.setFixedHeight(40)  # fixme
        # self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.NoWrap)
        # self.setLineWrapColumnOrWidth(10000)

        self.key_event_buffer = ""
        self.navigation_bar = None
        self.toolbar = None

        # self.cursorForPosition()
        # self.cursorPositionChanged()  (signal)

    # def keyPressEvent(self, event):
    #     """
    #     No direct text input!
    #     """
    #     event.ignore()

    def set_shortcuts(self):
        action = QAction()
        action.setShortcut(QKeySequence.Undo)
        action.triggered.connect(self.toolbar.undo_action.trigger)
        # shortcut = QShortcut(QKeySequence.Undo, self)
        # shortcut.activated.connect(self.toolbar.undo_action)

        # shortcut = QShortcut(QKeySequence.Undo, self)
        # shortcut.activated.connect(self.toolbar.undo_action.trigger)

    def keyPressEvent(self, event):
        """
        Take focus (from calculator_target) so that shortcuts to buttons
        work.
        """
        key = event.key()
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

        # QAction key sequences
        if key_sequence == QKeySequence.MoveToPreviousChar:
            self.navigation_bar.left_action.trigger()
            print("LEFT!")
        elif key_sequence == QKeySequence.MoveToNextChar:
            self.navigation_bar.right_action.trigger()
            print("RIGHT!")
        elif key_sequence == QKeySequence.Undo:
            self.toolbar.undo_action.trigger()
            print("UNDO !!")
        elif key_sequence == QKeySequence.Redo:
            self.toolbar.redo_action.trigger()

        # Text shortcuts
        text = event.text()
        if text:
            # FIXME: process more complex sequences (i.e. more than one letter)
            self.key_event_buffer += text
            yes = CalculatorButton.process_key_events(self.key_event_buffer)
            # if yes:
            self.key_event_buffer = ""

        event.ignore()

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


class CalculatorToolbar(QToolBar):
    def __init__(self):
        super().__init__()
        icons_dir = cdirs.icons

        self.rewind = QAction(QIcon(str((icons_dir /
                                     'goback-begining.png').resolve())),
                _('Undo all'), self)
        self.undo_action = QAction(QIcon(str((icons_dir /
                                          'undo_action.png').resolve())),
                _('Undo'), self)
        self.redo_action = QAction(QIcon(str((icons_dir /
                                          'redo_action.png').resolve())),
                _('Redo'), self)
        self.go_to_end = QAction(QIcon(str((icons_dir /
                                            'go-end-96.png').resolve())),
                _('Redo all'), self)

        self.delete = QAction(QIcon(str((icons_dir /
                                         'cancel.png').resolve())),
            _('Delete'), self)

        self.addAction(self.rewind)
        self.addAction(self.undo_action)
        self.addAction(self.redo_action)
        self.addAction(self.go_to_end)
        self.addSeparator()
        self.addAction(self.delete)

        # self.undo_action.setShortcut(QKeySequence.Undo)
        # self.redo_action.setShortcut(QKeySequence.Redo)
        # self.delete.setShortcut(QKeySequence.Delete)


class NavigationBar(QToolBar):
    """
    A toolbar with navigation buttons: left, up, right arrow.
    """
    def __init__(self):
        super().__init__()

        icons_dir = cdirs.icons

        self.left_action = QAction(_('Move left'), self)
        self.up_action = QAction(_('Move Up'), self)
        self.right_action = QAction(_('Move right'), self)

        # self.undo_action = QAction(QIcon(str((icons_dir /
        #                                   'undo_action.png').resolve())),
        #         _('Undo'), toolbar)
        self.addAction(self.left_action)
        self.addAction(self.up_action)
        self.addAction(self.right_action)

        # self.left_action.setShortcut(QKeySequence.MoveToPreviousChar)
        # self.up_action.setShortcut(QKeySequence.MoveToPreviousLine)
        # self.right_action.setShortcut(QKeySequence.MoveToNextChar)

        # TODO: connect / add Icons


class CalculatorButton(QToolButton):
    """
    A class to display a button associated to a (list of)
    MarkedPatternMathObjects. Pressing the button insert (one of) the pattern
    at the current cursor position in the MarkedPatternMathObject under
    construction.
    """

    send_pattern = Signal(MarkedPatternMathObject)

    shortcuts_dic = dict()

    def __init__(self, symbol):
        super().__init__()
        self.pattern_s = CalculatorPatternLines.marked_patterns[symbol]
        # self.setText(symbol)
        # self.clicked.connect(self.process_click)
        # self.add_shortcut(symbol)

        action = QAction(symbol)
        action.triggered.connect(self.process_click)
        letter = symbol[0]
        action.setShortcut(QKeySequence(letter))
        # action.setShortcutContext(action.shortcutContext().ApplicationShortcut)
        print(action.shortcutContext())
        self.setDefaultAction(action)

    def add_shortcut(self, parent):
        """
        Automatically add the first letter as a shortcut which is a child of
        parent.
        """

        letter = self.text()[0]
        if letter not in self.shortcuts_dic:
            ## shortcut = QShortcut(QKeySequence(letter), parent)
            ## shortcut.activated.connect(self.click)
            # self.setShortcut(QKeySequence(letter))
            ## shortcut.setContext(Qt.WidgetWithChildrenShortcut)
            ## if letter in ('1', '2', '3'):
            ##     self.setShortcut(QKeySequence('a'))
            ##     self.setShortcut(QKeySequence('\\, a'))
            self.shortcuts_dic[letter] = self
            # TODO: add latex shortcuts based on main symbol.

    # @Slot()
    # def click(self):
    #     self.animateClick(100)

    @Slot()
    def process_click(self):
        # print('clic')
        self.send_pattern.emit(self.pattern_s)

    @classmethod
    def process_key_events(cls, key_event_buffer):
        button = cls.shortcuts_dic.get(key_event_buffer)
        if button:
            button.animateClick(100)
            return True


class CalculatorButtons(QHBoxLayout):
    """
    A class to display a line of CalculatorButton.
    """

    def __init__(self, title: str, line: [str]):
        super().__init__()
        self.title = title
        self.line = line
        self.buttons = [CalculatorButton(symbol) for symbol in line]
        self.addStretch()
        for button in self.buttons:
            self.addWidget(button)
        self.addStretch()


class CalculatorMainWindow(QDialog):
    """
    A class to display a "calculator", i.e. a QWidget that enables usr to
    build a new MathObject (a new mathematical object or property).
    """

    send_pattern = Signal(MarkedPatternMathObject)

    def __init__(self, calc_patterns: [CalculatorPatternLines]):
        super().__init__()

        self.key_event_buffer = ""

        self.toolbar = CalculatorToolbar()

        # self.rewind = None
        # self.undo_action = None
        # self.redo_action = None
        # self.go_to_end = None
        # self.__init_toolbar()
        self.navigation_bar = NavigationBar()

        self.calculator_target = CalculatorTarget()
        self.calculator_target.navigation_bar = self.navigation_bar
        self.calculator_target.toolbar = self.toolbar
        self.calculator_target.set_shortcuts()

        main_lyt = QVBoxLayout()
        main_lyt.addWidget(self.toolbar)

        self.buttons_groups = []
        CalculatorButton.shortcuts_dic = {}
        self.btns_wgt = QWidget()
        btns_lyt = QVBoxLayout()
        for calc_pattern in calc_patterns:
            title = calc_pattern.title
            btns_lyt.addWidget(QLabel(calc_pattern.title + _(':')))
            for line in calc_pattern.lines:
                buttons_lyt = CalculatorButtons(title, line)
                # FIXME: improve UI1
                # main_lyt.addLayout(buttons_lyt)
                btns_lyt.addLayout(buttons_lyt)
                self.buttons_groups.append(buttons_lyt)
                for btn in buttons_lyt.buttons:
                    btn.add_shortcut(parent=self)

        self.btns_wgt.setLayout(btns_lyt)
        main_lyt.addWidget(self.btns_wgt)

        main_lyt.addWidget(self.calculator_target)
        self.lean_target_label = TargetLabel(None)
        main_lyt.addWidget(self.lean_target_label)

        self.setLayout(main_lyt)

        for btn in self.buttons():
            btn.send_pattern.connect(self.process_clic)

        # Navigation btns
        main_lyt.addWidget(self.navigation_bar)

        # OK / Cancel btns
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok
                                          | QDialogButtonBox.Cancel)
        main_lyt.addWidget(self.button_box)

        self.calculator_target.setFocus()
        # self.setFocus()

        # self.buttonBox.accepted.connect(self.accept)
        # self.buttonBox.rejected.connect(self.reject)

    # def keyPressEvent(self, event):
    #     """
    #     Take focus (from calculator_target) so that shortcuts to buttons
    #     work.
    #     """
    #     # self.setFocus()
    #     # super().keyPressEvent(event)
    #     # TODO: add timer singleshot --> calculator_target.setFocus()
    #     # event.ignore()
    #     text = event.text()
    #     if text:
    #         self.key_event_buffer += text
    #         yes = CalculatorButton.process_key_events(self.key_event_buffer)
    #         # if yes:
    #         self.key_event_buffer = ""
    #     elif event.key() == Qt.Key_Left:
    #         self.navigation_bar.left_action.trigger()
    #     if event.modifiers() & Qt.ControlModifier:
    #         if event.key() == Qt.Key_Undo:
    #         self.undo_action.trigger()

    def buttons(self) -> [CalculatorButton]:
        btns = []
        for buttons_group in self.buttons_groups:
            btns.extend(buttons_group.buttons)
        return btns

    # def set_target(self, target):
    #     target = PatternMathObject(node='MVAR', info={}, children=[],
    #                                math_type=target)
    #     text = target.math_type_to_display(format_='html')
    #
    #     self.calculator_target.setHtml(text)
        # self.lean_target_label.set_target(target, format_='lean')

    def set_html(self, text):
        self.calculator_target.setHtml(text)

    @Slot()
    def process_clic(self, pattern):
        self.send_pattern.emit(pattern)

    # def __init_toolbar(self):
        # icons_base_dir = cvars.get("icons.path")
        # icons_dir = fs.path_helper(icons_base_dir)
        # icons_dir = cdirs.icons
        # toolbar = self.toolbar
        #
        # self.rewind = QAction(QIcon(str((icons_dir /
        #                              'goback-begining.png').resolve())),
        #         _('Undo all'), toolbar)
        # self.undo_action = QAction(QIcon(str((icons_dir /
        #                                   'undo_action.png').resolve())),
        #         _('Undo'), toolbar)
        # self.redo_action = QAction(QIcon(str((icons_dir /
        #                                   'redo_action.png').resolve())),
        #         _('Redo'), toolbar)
        # self.go_to_end = QAction(QIcon(str((icons_dir /
        #                                     'go-end-96.png').resolve())),
        #         _('Redo all'), toolbar)
        #
        # self.delete = QAction(QIcon(str((icons_dir /
        #                                  'cancel.png').resolve())),
        #     _('Delete'), toolbar)
        # toolbar.addAction(self.rewind)
        # toolbar.addAction(self.undo_action)
        # toolbar.addAction(self.redo_action)
        # toolbar.addAction(self.go_to_end)
        # toolbar.addSeparator()
        # toolbar.addAction(self.delete)
        #
        # # self.undo_action.setShortcut(QKeySequence.Undo)
        # # self.redo_action.setShortcut(QKeySequence.Redo)
        # # self.delete.setShortcut(QKeySequence.Delete)
        #


class CalculatorController:
    """
    The calculator controller. This is initiated with
    - a MarkedPatternMathObject, typically just a Metavar, that stands for
    the object under construction.
    - a dictionary of CalculatorGroup instances, that is used to build the
    various buttons groups.
    """

    def __init__(self, target: MarkedPatternMathObject,
                 context=None,
                 calculator_groups=None):
        self.target = target
        self.history: [MarkedPatternMathObject] = []
        self.history_idx = -1
        if calculator_groups:
            self.calculator_groups = calculator_groups
        else:  # Standard groups
            self.calculator_groups = [calculator_group, sci_calc_group,
                                      logic_group,
                                      set_theory_group]

        self.calculator_ui = CalculatorMainWindow(self.calculator_groups)
        # self.calculator_ui.set_target(target)
        self.calculator_ui.send_pattern.connect(self.insert_pattern)

        self.__init_signals()
        self.update()  # Display target and create first history entry

    def __init_signals(self):
        calc_ui = self.calculator_ui
        calc_ui.toolbar.rewind.triggered.connect(self.history_to_beginning)
        calc_ui.toolbar.undo_action.triggered.connect(self.history_undo)
        calc_ui.toolbar.redo_action.triggered.connect(self.history_redo)
        calc_ui.toolbar.go_to_end.triggered.connect(self.history_to_end)
        calc_ui.toolbar.delete.triggered.connect(self.delete)

        calc_ui.navigation_bar.left_action.triggered.connect(self.move_left)
        calc_ui.navigation_bar.up_action.triggered.connect(self.move_up)
        calc_ui.navigation_bar.right_action.triggered.connect(self.move_right)

    def show(self):
        self.calculator_ui.show()

    @property
    def html_target(self):
        # target = PatternMathObject(node='MVAR', info={}, children=[],
        #                            math_type=target)
        text = self.target.to_display(format_='html')
        return text

    def virtual_cursor_position(self):
        """
        Return the position at which the cursor should be seen, corresponding to
        the current marked node of self.target, if any, or the end.
        """
        doc = QTextDocument()
        MathDisplay.mark_cursor = True
        doc.setHtml(self.html_target)
        text = doc.toPlainText()
        position = text.find(MathDisplay.cursor_tag)

        MathDisplay.mark_cursor = False
        return position

    def update_cursor(self):
        # self.calculator_ui.calculator_target.setFocus()
        position = self.virtual_cursor_position()
        self.calculator_ui.calculator_target.go_to_position(position)

    def update(self):
        """
        Update target display, and store it in history.
        Delete the end of history if any.
        """

        self.history_idx += 1
        # self.calculator_ui.set_target(self.target)
        self.history = self.history[:self.history_idx]
        self.history.append(self.target)

        self.calculator_ui.set_html(self.html_target)
        self.update_cursor()
        # print(self.calculator_ui.calculator_target.document().toHtml())
        # print(self.calculator_ui.calculator_target.document().toPlainText())
        # print(self.calculator_ui.calculator_target.document().toPlainText())

    @Slot()
    def insert_pattern(self, pattern_s):
        # Fixme: pattern or patterns?
        new_target = self.target.deep_copy(self.target)
        ok = new_target.insert(pattern_s)
        print(new_target)
        if ok:
            self.target = new_target
            self.target.move_after_insert()
            self.update()

        print(ok)
        print(self.target)
        # print(self.target.math_type)

    def history_update(self):
        """
        Update after a history move.
        """
        self.target = self.history[self.history_idx]
        self.calculator_ui.set_html(self.html_target)
        print(self.target)
        # print(self.target.math_type)

        self.update_cursor()

        # TODO: enable/disable buttons

    @Slot()
    def history_undo(self):
        if self.history_idx > 0:
            self.history_idx -= 1
            self.history_update()

    @Slot()
    def history_redo(self):
        if self.history_idx < len(self.history) - 1:
            self.history_idx += 1
            self.history_update()

    @Slot()
    def history_to_beginning(self):
        self.history_idx = 0
        self.history_update()

    @Slot()
    def history_to_end(self):
        self.history_idx = len(self.history) - 1
        self.history_update()

    @Slot()
    def delete(self):
        success = self.target.delete()
        if success:
            self.update()

    @Slot()
    def move_right(self):
        self.target.move_right()
        self.calculator_ui.set_html(self.html_target)
        # print(self.target)
        print(self.target)
        self.update_cursor()

    @Slot()
    def move_left(self):
        self.target.move_left()
        self.calculator_ui.set_html(self.html_target)
        # print(self.target)
        print(self.target)
        self.update_cursor()

    @Slot()
    def move_up(self):
        if self.target.move_up():
            self.calculator_ui.set_html(self.html_target)
            # print(self.target)
            # print(self.target.math_type)
        self.update_cursor()


def main():

    target = MarkedPatternMathObject.from_string('?0: CONSTANT/name=ℝ')
    target.mark()
    app = QApplication([])
    calculator = CalculatorController(target=target)

    calculator.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()






