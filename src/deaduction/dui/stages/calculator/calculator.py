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

from PySide2.QtCore import Signal, Slot, Qt
from PySide2.QtGui     import  QKeySequence, QIcon
from PySide2.QtWidgets import (QApplication, QWidget, QPushButton, QToolButton,
                               QHBoxLayout, QVBoxLayout, QLabel, QToolBar,
                               QAction, QDialog, QDialogButtonBox)

import deaduction.pylib.config.vars as cvars
import deaduction.pylib.config.dirs as cdirs
import deaduction.pylib.utils.filesystem as fs

from deaduction.pylib.pattern_math_obj import (PatternMathObject,
                                               MarkedPatternMathObject,
                                               MarkedMetavar,
                                               CalculatorPatternLines,
                                               calculator_group,
                                               sci_calc_group,
                                               logic_group,
                                               set_theory_group)

from deaduction.dui.elements import TargetLabel

global _
log = logging.getLogger(__name__)


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

        self.left_action.setShortcut(QKeySequence.MoveToPreviousChar)
        self.up_action.setShortcut(QKeySequence.MoveToPreviousLine)
        self.right_action.setShortcut(QKeySequence.MoveToNextChar)


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
        self.setText(symbol)
        self.clicked.connect(self.process_click)
        letter = symbol[0]
        if letter not in self.shortcuts_dic:
            self.setShortcut(QKeySequence(letter))
            self.shortcuts_dic[letter] = self

    @Slot()
    def process_click(self):
        # print('clic')
        self.send_pattern.emit(self.pattern_s)


class CalculatorButtons(QHBoxLayout):
    """
    A class to display a line of CalculatorButton.
    """

    def __init__(self, title: str, line: [str]):
        super().__init__()
        self.title = title
        self.line = line
        self.buttons = [CalculatorButton(symbol) for symbol in line]
        for button in self.buttons:
            self.addWidget(button)


class CalculatorMainWindow(QDialog):
    """
    A class to display a "calculator", i.e. a QWidget that enables usr to
    build a new MathObject (a new mathematical object or property).
    """

    send_pattern = Signal(MarkedPatternMathObject)

    def __init__(self, calc_patterns: [CalculatorPatternLines]):
        super().__init__()
        self.toolbar = QToolBar()
        self.rewind = None
        self.undo_action = None
        self.redo_action = None
        self.go_to_end = None
        self.__init_toolbar()
        self.navigation_bar = NavigationBar()

        main_lyt = QVBoxLayout()
        main_lyt.addWidget(self.toolbar)

        self.buttons_groups = []
        for calc_pattern in calc_patterns:
            title = calc_pattern.title
            main_lyt.addWidget(QLabel(calc_pattern.title + _(':')))
            for line in calc_pattern.lines:
                buttons_lyt = CalculatorButtons(title, line)
                # FIXME: improve UI
                main_lyt.addLayout(buttons_lyt)
                self.buttons_groups.append(buttons_lyt)

        self.target_label = TargetLabel(None)
        main_lyt.addWidget(self.target_label)
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
        # self.buttonBox.accepted.connect(self.accept)
        # self.buttonBox.rejected.connect(self.reject)

    def buttons(self) -> [CalculatorButton]:
        btns = []
        for buttons_group in self.buttons_groups:
            btns.extend(buttons_group.buttons)
        return btns

    def set_target(self, target):
        target = PatternMathObject(node='MVAR', info={}, children=[],
                                   math_type=target)
        self.target_label.set_target(target)
        # self.lean_target_label.set_target(target, format_='lean')

    @Slot()
    def process_clic(self, pattern):
        self.send_pattern.emit(pattern)

    def __init_toolbar(self):
        # icons_base_dir = cvars.get("icons.path")
        # icons_dir = fs.path_helper(icons_base_dir)
        icons_dir = cdirs.icons
        toolbar = self.toolbar

        self.rewind = QAction(QIcon(str((icons_dir /
                                     'goback-begining.png').resolve())),
                _('Undo all'), toolbar)
        self.undo_action = QAction(QIcon(str((icons_dir /
                                          'undo_action.png').resolve())),
                _('Undo'), toolbar)
        self.redo_action = QAction(QIcon(str((icons_dir /
                                          'redo_action.png').resolve())),
                _('Redo'), toolbar)
        self.go_to_end = QAction(QIcon(str((icons_dir /
                                            'go-end-96.png').resolve())),
                _('Redo all'), toolbar)

        self.delete = QAction(QIcon(str((icons_dir /
                                         'cancel.png').resolve())),
            _('Delete'), toolbar)
        toolbar.addAction(self.rewind)
        toolbar.addAction(self.undo_action)
        toolbar.addAction(self.redo_action)
        toolbar.addAction(self.go_to_end)
        toolbar.addSeparator()
        toolbar.addAction(self.delete)

        self.undo_action.setShortcut(QKeySequence.Undo)
        self.redo_action.setShortcut(QKeySequence.Redo)
        self.delete.setShortcut(QKeySequence.Delete)


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
        calc_ui.rewind.triggered.connect(self.history_to_beginning)
        calc_ui.undo_action.triggered.connect(self.history_undo)
        calc_ui.redo_action.triggered.connect(self.history_redo)
        calc_ui.go_to_end.triggered.connect(self.history_to_end)
        calc_ui.delete.triggered.connect(self.delete)

    def show(self):
        self.calculator_ui.show()

    def update(self):
        """
        Update target display, and store it in history.
        Delete the end of history if any.
        """

        self.history_idx += 1
        self.calculator_ui.set_target(self.target)
        self.history = self.history[:self.history_idx]
        self.history.append(self.target)
        self.calculator_ui.target_label.setFocus()

    @Slot()
    def insert_pattern(self, pattern_s):
        # Fixme: pattern or patterns?
        new_target = self.target.deep_copy(self.target)
        ok = new_target.insert_at_marked_mvar(pattern_s)
        print(new_target)
        if ok:
            self.target = new_target
            self.target.move_right(to_unmatched_mvar=True)
            self.update()

        print(ok)
        print(self.target)
        print(self.target.math_type)

    def history_update(self):
        """
        Update after a history move.
        """
        self.target = self.history[self.history_idx]
        self.calculator_ui.set_target(self.target)

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


def main():

    target = MarkedPatternMathObject.from_string('?0: CONSTANT/name=ℝ')
    target.mark()
    app = QApplication([])
    calculator = CalculatorController(target=target)

    calculator.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()






