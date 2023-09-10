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

from PySide2.QtCore import Signal, Slot, Qt, QTimer
from PySide2.QtGui     import  QKeySequence, QIcon, QTextDocument
from PySide2.QtWidgets import (QApplication, QTextEdit, QToolButton, QWidget,
                               QPushButton,
                               QHBoxLayout, QVBoxLayout, QGridLayout,
                               QLabel, QToolBar,
                               QAction, QDialog, QDialogButtonBox,
                               QCheckBox)

import deaduction.pylib.config.vars as cvars
import deaduction.pylib.config.dirs as cdirs
import deaduction.pylib.utils.filesystem as fs

from deaduction.pylib.math_display import MathDisplay
from deaduction.pylib.math_display.nodes import (Node, LogicalNode,
                                                 SetTheoryNode, NumberNode)

from deaduction.pylib.pattern_math_obj import (PatternMathObject,
                                               MarkedPatternMathObject,
                                               MarkedMetavar,
                                               MetaVar,
                                               CalculatorPatternLines,
                                               calc_shortcuts,
                                               calculator_group,
                                               sci_calc_group)
from deaduction.pylib.pattern_math_obj.calculator_pattern_strings import CalculatorAbstractButton

from deaduction.dui.primitives.base_math_widgets_styling import MathTextWidget
from deaduction.dui.primitives          import deaduction_fonts


global _
log = logging.getLogger(__name__)

if __name__ == "__main__":
    from deaduction.pylib import logger
    logger.configure(domains="deaduction",
                     display_level="debug",
                     filename=None)


Node.PatternMathObject = PatternMathObject
Node.MarkedPatternMathObject = MarkedPatternMathObject


class CalculatorTarget(MathTextWidget):

    def __init__(self):
        super().__init__()
        self.set_highlight(True)

        self.setFixedHeight(40)  # fixme
        # self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.NoWrap)
        # self.setLineWrapColumnOrWidth(10000)

        self.key_event_buffer = ""
        self.navigation_bar = None
        self.toolbar = None
        self.button_box = None

        self.key_buffer_timer = QTimer()
        self.key_buffer_timer.setSingleShot(True)
        self.key_buffer_timer.timeout.connect(self.clear_key_buffer)
        # self.cursorForPosition()
        # self.cursorPositionChanged()  (signal)

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
        # elif key_sequence == QKeySequence.Delete:
        #     bar = self.toolbar
        #     action = bar.delete

        if bar and action:
            bar.animate_click(action)
            self.clear_key_buffer()
            event.ignore()
            return

        # Text shortcuts
        text = event.text()
        if text:
            # FIXME: process more complex sequences (i.e. more than one letter)
            self.key_event_buffer += text
            # print(self.key_event_buffer, self.key_buffer_timer)
            yes = CalculatorButton.process_key_events(self.key_event_buffer)
            if yes:
                self.clear_key_buffer()

        event.ignore()

    @Slot()
    def clear_key_buffer(self):
        self.key_event_buffer = ""

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


class AbstractToolBar(QToolBar):

    def animate_click(self, action: QAction):
        """
        Simulate a click on the tool button corresponding to the QAction.
        """
        button = self.widgetForAction(action)
        button.animateClick(100)


class CalculatorToolbar(AbstractToolBar):
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

        # self.delete = QAction(QIcon(str((icons_dir /
        #                                  'cancel.png').resolve())),
        #     _('Delete'), self)

        self.addAction(self.rewind)
        self.addAction(self.undo_action)
        self.addAction(self.redo_action)
        self.addAction(self.go_to_end)
        # self.addSeparator()
        # self.addAction(self.delete)


class NavigationBar(AbstractToolBar):
    """
    A toolbar with navigation buttons: left, up, right arrow.
    """
    def __init__(self):
        super().__init__()
        self.setLayoutDirection(Qt.RightToLeft)

        self.lean_mode_wdg = QCheckBox("Lean mode")
        self.lean_mode_wdg.setFocusPolicy(Qt.NoFocus)
        self.addWidget(self.lean_mode_wdg)
        self.addSeparator()
        icons_dir = cdirs.icons
        # TODO: add icons

        beg_path = str((icons_dir / 'icons8-double-left-48.png').resolve())
        self.beginning_action = QAction(QIcon(beg_path),
                                        _('Go to beginning'), self)

        # self.left_unassigned_action = QAction(_('?←'), self)

        left_path = str((icons_dir / 'icons8-back-48.png').resolve())
        self.left_action = QAction(QIcon(left_path),
                                   _('Move left'), self)

        up_path = str((icons_dir /
                      'icons8-thick-arrow-pointing-up-48.png').resolve())
        self.up_action = QAction(QIcon(up_path), _('Move up'), self)

        right_path = str((icons_dir / 'icons8-forward-48.png').resolve())
        self.right_action = QAction(QIcon(right_path),
                                   _('Move right'), self)

        # self.right_unassigned_action = QAction(_('→?'), self)

        end_path = str((icons_dir / 'icons8-double-right-48.png').resolve())
        self.end_action = QAction(QIcon(end_path),
                                   _('Go to end'), self)

        self.delete = QAction(QIcon(str((icons_dir /
                                         'icons8-clear-48.png').resolve())),
                              _('Delete'), self)

        self.addAction(self.delete)
        self.addAction(self.end_action)
        # self.addAction(self.right_unassigned_action)
        self.addAction(self.right_action)
        self.addAction(self.up_action)
        self.addAction(self.left_action)
        # self.addAction(self.left_unassigned_action)
        self.addAction(self.beginning_action)


class CalculatorButton(QToolButton, CalculatorAbstractButton):
    """
    A class to display a button associated to a (list of)
    MarkedPatternMathObjects. Pressing the button insert (one of) the pattern
    at the current cursor position in the MarkedPatternMathObject under
    construction.
    """

    send_pattern = Signal(MarkedPatternMathObject)

    shortcuts_dic = dict()

    def __init__(self, symbol, tooltip=None, patterns=None, menu=False):
        super().__init__()
        CalculatorAbstractButton.__init__(self, symbol, tooltip, patterns, menu)
        # self.patterns = CalculatorPatternLines.marked_patterns[symbol]

        action = QAction(self.symbol)
        action.triggered.connect(self.process_click)
        self.setDefaultAction(action)
        if self.tooltip:
            self.setToolTip(self.tooltip)
        self.add_shortcut()

        symbol_size = deaduction_fonts.symbol_button_font_size
        self.setFont(deaduction_fonts.math_fonts(size=symbol_size))

    def add_shortcut(self):
        """
        Automatically add self.text() as a shortcut for self.
        """

        self.shortcuts_dic[self.text()] = self

    @classmethod
    def find_shortcut(cls, text_buffer):
        # FIXME: not optimal
        match = [key for key in cls.shortcuts_dic if key.startswith(text_buffer)]
        more_match = [calc_shortcuts[key] for key in calc_shortcuts
                      if key.startswith(text_buffer)
                      and calc_shortcuts[key] in cls.shortcuts_dic]
        match += more_match
        if len(match) == 1:
            return cls.shortcuts_dic[match[0]]
        elif len(match) > 1:
            # OK if all shortcuts refer to the same text
            first_match = match[0]
            test = all(cls.shortcuts_dic[other_match].text() ==
                       cls.shortcuts_dic[first_match].text()
                       for other_match in match[1:])
            if test:
                # Several match of 'the same' button
                return cls.shortcuts_dic[match[0]]

    @Slot()
    def process_click(self):
        """
        Send a signal so that Calculator process the click.
        """
        self.send_pattern.emit(self.patterns)

    @classmethod
    def process_key_events(cls, key_event_buffer):
        # button = cls.shortcuts_dic.get(key_event_buffer)
        button = cls.find_shortcut(key_event_buffer)
        if button:
            button.animateClick(100)
            return True


class CalculatorButtonsGroup(QWidget):
    """
    A widget to display a list of CalculatorButtons, with a title and a
    disclosure triangle.
    """

    def __init__(self, title, calculator_buttons: [CalculatorButton],
                 col_size):
        super().__init__()
        self.title = title
        self.col_size = col_size
        self.buttons = calculator_buttons

        self.title_label = QLabel(self.title + _(':'))
        self.buttons_layout = QGridLayout()
        self.include_buttons()
        self.margin_btns_lyt = QHBoxLayout()
        self.margin_btns_lyt.addStretch()
        self.margin_btns_lyt.addLayout(self.buttons_layout)
        self.margin_btns_lyt.addStretch()

        # Fill-in main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.title_label)
        main_layout.addLayout(self.margin_btns_lyt)
        self.setLayout(main_layout)

    def include_buttons(self):
        """
        Add self's buttons is self.buttons_layout
        """

        for line in range(len(self.buttons) // self.col_size + 1):
            col = 0
            for button in self.buttons[self.col_size * line:
                                       self.col_size * (line + 1)]:
                self.buttons_layout.addWidget(button, line, col)
                col += 1

    @classmethod
    def from_node_subclass(cls, node_class, col_size=4):
        """
        Construct a CalculatorButtonsGroup from instances of a Node subclass.
        Here node_class should be, for instance LogicalNode.
        """
        buttons = [CalculatorButton.from_node(node)
                   for node in node_class.calculator_nodes]
        buttons_group = cls(title=node_class.name,
                            calculator_buttons=buttons,
                            col_size=col_size)
        return buttons_group


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

    def from_calculator_pattern_lines(self):
        pass


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
        self.navigation_bar = NavigationBar()

        # Init target as a QTextedit
        # calculator_target will process key events and send them to the
        # toolbars

        main_lyt = QVBoxLayout()
        main_lyt.addWidget(self.toolbar)

        self.buttons_groups = []
        # Clear ancient shortcuts!!
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

        for NodeClass, col_size in (  (LogicalNode, 5),
                                      # (SetTheoryNode, 5),
                                    (NumberNode, 4), ):
            buttons = CalculatorButtonsGroup.from_node_subclass(NodeClass,
                                                                col_size)
            btns_lyt.addWidget(buttons)
            self.buttons_groups.append(buttons)

        self.btns_wgt.setLayout(btns_lyt)
        main_lyt.addWidget(self.btns_wgt)

        # CalculatorTarget
        self.calculator_target = CalculatorTarget()
        self.calculator_target_title = QLabel()
        main_lyt.addWidget(self.calculator_target_title)
        main_lyt.addWidget(self.calculator_target)

        self.setLayout(main_lyt)

        for btn in self.buttons():
            btn.send_pattern.connect(self.process_clic)

        # Navigation btns
        main_lyt.addWidget(self.navigation_bar)

        # OK / Cancel btns
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok)
                                           # | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        main_lyt.addWidget(self.button_box)

        # Connect calculator_target
        self.calculator_target.navigation_bar = self.navigation_bar
        self.calculator_target.toolbar = self.toolbar
        self.calculator_target.button_box = self.button_box
        self.calculator_target.setFocus()

    def set_target_title(self, title):
        self.calculator_target_title.setText(title)

    def buttons(self) -> [CalculatorButton]:
        btns = []
        for buttons_group in self.buttons_groups:
            btns.extend(buttons_group.buttons)
        return btns

    def set_html(self, text):
        self.calculator_target.setHtml(text)

    @Slot()
    def process_clic(self, pattern):
        self.send_pattern.emit(pattern)


class CalculatorController:
    """
    The calculator controller. This is initiated with
    - a MarkedPatternMathObject, typically just a Metavar, that stands for
    the object under construction.
    - a dictionary of CalculatorGroup instances, that is used to build the
    various buttons groups.
    """

    def __init__(self, target_type=None,
                 context=None,
                 calculator_groups=None,
                 title="Calculator"):

        if not target_type:
            target_type = MetaVar()
            p_target_type = MarkedPatternMathObject.from_pattern_math_object(
                target_type)
        else:
            p_target_type = MarkedPatternMathObject.from_math_object(target_type)

        target_mvar = MetaVar(math_type=p_target_type)
        self.target = MarkedMetavar.from_mvar(target_mvar)  # FIXME!!!!!!!!
        self.target.mark()
        display_type = target_type.math_type_to_display(format_="utf8",
                                                        is_math_type=True,
                                                        text=True)
        self.target_title = _("Enter") + " " + display_type

        self.calculator_groups = []
        if context:
            context_line = CalculatorPatternLines.from_context(context)
            self.calculator_groups.append(context_line)
            # Compute applications on ContextMathObjects:
            MarkedPatternMathObject.populate_applications_from_context(context)

        if calculator_groups:
            self.calculator_groups.extend(calculator_groups)
        # else:  # Standard groups
        #     self.calculator_groups.extend([calculator_group, sci_calc_group])

        cpls = CalculatorPatternLines.constants_from_definitions()
        self.calculator_groups.extend(cpls)

        self.history: [MarkedPatternMathObject] = []
        self.history_idx = -1

        self.calculator_ui = CalculatorMainWindow(self.calculator_groups)
        self.calculator_ui.setWindowTitle(title)
        self.calculator_ui.set_target_title(self.target_title)
        # self.calculator_ui.set_target(target)
        self.calculator_ui.send_pattern.connect(self.insert_pattern)

        self.__init_signals()
        self.update()  # Display target and create first history entry

    def __init_signals(self):
        calc_ui = self.calculator_ui

        t_bar = calc_ui.toolbar
        t_bar.rewind.triggered.connect(self.history_to_beginning)
        t_bar.undo_action.triggered.connect(self.history_undo)
        t_bar.redo_action.triggered.connect(self.history_redo)
        t_bar.go_to_end.triggered.connect(self.history_to_end)

        n_bar = calc_ui.navigation_bar
        n_bar.beginning_action.triggered.connect(self.go_to_beginning)
        # n_bar.left_unassigned_action.triggered.connect(
        #     self.move_to_previous_unassigned)
        n_bar.left_action.triggered.connect(self.move_left)
        n_bar.up_action.triggered.connect(self.move_up)
        n_bar.right_action.triggered.connect(self.move_right)
        # n_bar.right_unassigned_action.triggered.connect(
        #     self.move_to_next_unassigned)
        n_bar.end_action.triggered.connect(self.go_to_end)
        n_bar.lean_mode_wdg.stateChanged.connect(self.set_lean_mode)
        n_bar.delete.triggered.connect(self.delete)

    def show(self):
        self.calculator_ui.show()

    @classmethod
    def get_item(cls, context, target_type, title) -> (Union[PatternMathObject,
                                                             str],
                                                       bool):
        """
        Execute a CalculatorController and send the choice.
        The choice is either a PatternMathObject to be converted to Lean code,
        or a string (of Lean code) if the calculator i in Lean mode.
        """

        if target_type:
            log.debug(f"Calculator with target type = "
                      f"{target_type.to_display(format_='utf8')}")
        calculator_controller = cls(context=context,
                                    target_type=target_type,
                                    title=title)
        # Execute the ButtonsDialog and wait for results
        OK = calculator_controller.calculator_ui.exec()

        # After exec
        choice = calculator_controller.target
        choice.unmark()
        choice = MarkedPatternMathObject.generic_parentheses(choice.assigned_math_object)

        if calculator_controller.lean_mode:
            choice = calculator_controller.calculator_ui.calculator_target.toPlainText()
        return choice, OK

    @Slot()
    def set_lean_mode(self):
        self.calculator_ui.calculator_target.lean_mode = self.lean_mode
        self.set_target()

    @property
    def lean_mode(self) -> bool:
        mode = self.calculator_ui.navigation_bar.lean_mode_wdg.isChecked()
        return mode

    @property
    def html_target(self):
        if self.lean_mode:
            text = self.target.to_display(format_='lean')
        else:
            text = self.target.to_display(format_='html')
        return text

    @property
    def beginning_action(self):
        return self.calculator_ui.navigation_bar.beginning_action

    # @property
    # def left_unassigned_action(self):
    #     return self.calculator_ui.navigation_bar.left_unassigned_action

    @property
    def left_action(self):
        return self.calculator_ui.navigation_bar.left_action

    @property
    def up_action(self):
        return self.calculator_ui.navigation_bar.up_action

    @property
    def right_action(self):
        return self.calculator_ui.navigation_bar.right_action

    # @property
    # def right_unassigned_action(self):
    #     return self.calculator_ui.navigation_bar.right_unassigned_action

    @property
    def end_action(self):
        return self.calculator_ui.navigation_bar.end_action

    @property
    def undo_action(self):
        return self.calculator_ui.toolbar.undo_action

    @property
    def redo_action(self):
        return self.calculator_ui.toolbar.redo_action

    @Slot()
    def set_target(self):
        self.calculator_ui.set_html(self.html_target)

    def virtual_cursor_position(self):
        """
        Return the position at which the cursor should be seen, corresponding to
        the current marked node of self.target, if any, or the end.
        FIXME: probably not accurate, e.g. with subscript?
        """
        # Fixme: take cursor pos into account
        doc = QTextDocument()
        MathDisplay.mark_cursor = True
        # MathDisplay.cursor_pos = self.target.marked_descendant().cursor_pos
        doc.setHtml(self.html_target)
        text = doc.toPlainText()
        position = text.find(MathDisplay.cursor_tag)

        MathDisplay.mark_cursor = False
        # MathDisplay.cursor_pos = None
        return position

    def update_cursor(self):
        # self.target.adjust_cursor_pos()
        # self.calculator_ui.calculator_target.setFocus()
        position = self.virtual_cursor_position()
        self.calculator_ui.calculator_target.go_to_position(position)

    def enable_actions(self):
        target = self.target
        self.beginning_action.setEnabled(not target.is_at_beginning())
        # self.left_unassigned_action.setEnabled(bool(target.previous_unassigned()))
        self.left_action.setEnabled(not target.is_at_beginning())
        self.up_action.setEnabled(bool(target.parent_of_marked()))
        self.right_action.setEnabled(not target.is_at_end())
        # self.right_unassigned_action.setEnabled(bool(target.next_unassigned()))
        self.end_action.setEnabled(not target.is_at_end())
        self.undo_action.setEnabled(self.history_idx > 0)
        self.redo_action.setEnabled(self.history_idx < len(self.history) - 1)

    def update_cursor_and_enable_actions(self):
        self.update_cursor()
        self.enable_actions()
        print(self.target)

    def set_target_and_update(self):
        self.set_target()
        self.update_cursor_and_enable_actions()

    ##################
    # Target editing #
    ##################

    def update(self):
        """
        Update target display, and store it in history.
        Delete the end of history if any.
        This is called after insert_pattern() and delete() methods.
        """

        self.history_idx += 1
        # self.calculator_ui.set_target(self.target)
        self.history = self.history[:self.history_idx]
        self.history.append(self.target)
        self.set_target_and_update()
        # print( self.calculator_ui.calculator_target.document().toHtml())
        # print(self.calculator_ui.calculator_target.document().toPlainText())
        # print(self.calculator_ui.calculator_target.document().toPlainText())

    @Slot()
    def insert_pattern(self, pattern_s):
        """
        Try to insert pattern (or patterns) in self.target.
        If several patterns are provided, they are tried in order until
        success. If no success, generic insert is applied.
        Then an automatic insertion may happen.
        """

        new_target = self.target.deep_copy(self.target)
        assigned_mvar = None
                
        if not isinstance(pattern_s, list):
            pattern_s = [pattern_s]
            
        # (1) Special buttons: parentheses
        # FIXME!!
        if pattern_s[0].node == "GENERIC_PARENTHESES":
            assigned_mvar = new_target.insert_app_parentheses()

        # (2) Normal insert
        if not assigned_mvar:
            for pattern in pattern_s:
                assigned_mvar = new_target.insert(pattern)
                if assigned_mvar:
                    break

        # (3) Force insertion
        if not assigned_mvar:
            pattern = pattern_s[-1]  # FIXME, why not 0 ??
            assigned_mvar = new_target.generic_insert(pattern)

        print(f"New target: {new_target}")
        if assigned_mvar:
            self.target = new_target
            self.target.move_after_insert(assigned_mvar)
            self.update()

        print(f"New target after move: {new_target}")
        total, cursor = self.target.total_and_cursor_list()
        print("Total and cursor lists:")
        print(total)
        print(cursor)
        # print(self.target.math_type)

    @Slot()
    def delete(self):
        new_target = self.target.deep_copy(self.target)
        success = new_target.clear_marked_mvar()
        # print(new_target)
        if success:
            self.target = new_target
            # if not self.target.is_at_beginning():
            #     self.target.decrease_cursor_pos()
            self.update()

    #################
    # History moves #
    #################

    def history_update(self):
        """
        Update after a history move.
        """
        self.target = self.history[self.history_idx]
        self.set_target_and_update()
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

    ################
    # Cursor moves #
    ################

    @Slot()
    def move_right(self):
        # TODO: repeat if actual cursor do not move
        self.target.increase_cursor_pos()
        self.set_target_and_update()

    @Slot()
    def move_left(self):
        self.target.decrease_cursor_pos()
        self.set_target_and_update()

    @Slot()
    def go_to_beginning(self):
        self.target.go_to_beginning()
        self.set_target_and_update()

    @Slot()
    def go_to_end(self):
        self.target.go_to_end()
        self.set_target_and_update()

    @Slot()
    def move_to_next_unassigned(self):
        success = self.target.move_right_to_next_unassigned()
        if success:
            self.calculator_ui.set_html(self.html_target)
            self.set_target_and_update()

    @Slot()
    def move_to_previous_unassigned(self):
        success = self.target.move_left_to_previous_unassigned()
        if success:
            self.set_target_and_update()

    @Slot()
    def move_up(self):
        success = self.target.move_up()
        if success:
            self.set_target_and_update()


def main():

    from deaduction.pylib.mathobj import MathObject
    target = MarkedPatternMathObject.from_string('?0: SET(?1)')
    target = MarkedPatternMathObject.from_string('?0: *NUMBER_TYPES')
    # target.mark()
    app = QApplication([])
    # calculator = CalculatorController(target=target)
    # calculator.show()

    # target_type = MarkedPatternMathObject.from_string('SET(?1)')
    # target_type = MarkedPatternMathObject.from_string('*NUMBER_TYPES')
    # target_type = MarkedPatternMathObject.from_string('CONSTANT/name=ℝ')
    # target_type = MathObject(node="CONSTANT", info = {'name': 'ℝ'},
    #                          children=[])

    type_ = MathObject(node='TYPE', info={}, children=[])
    set_ = MathObject(node='CONSTANT', info={'name': 'X'}, children=[],
                      math_type=type_)
    target_type = MathObject(node="SET", info={},
                             children=[set_])
    target_type = MathObject(node="CONSTANT", info={'name': 'ℝ'},
                             children=[])
    choice, ok = CalculatorController.get_item(context=None,
                                               target_type=target_type,
                                               title='Essai')

    # sys.exit(app.exec_())
    print(ok, choice)
    if isinstance(choice, str):
        print(choice)
    else:
        print(choice.to_display(format_='lean'))


if __name__ == '__main__':
    main()






