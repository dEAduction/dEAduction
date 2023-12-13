"""
calculator.py : provide the Calculator and CalculatorWindow class.

The calculator enables usr to construct mathematical objects that will be
translated into Lean code. The interface tries to echo the global interface,
with
- a target area where the object under construction is shown; this is a
QTextEdit whose keyEvents are hacked to call buttons.
- ButtonGroups, where each button allows to insert some math patterns.
There are 3 kinds of buttons:
    (1) Usual buttons are provided by the Node class
e.g. 1, +, <=>, and so on
    (2) Context buttons are associated to context objects
    (3) Definitions buttons are associated to definitions from the current Lean
    file. These are built from Lean constants, the condition for a constant
    to gives rise to a button is to be present both in a definition statement
    of the currentLean file, and in one of the PatternMathDisplay
    dictionaries.

Furthermore, there are a special button who are associated to
GENERIC_APPLICATION, whose symbol is f(·). When pushed,
the calculator tried to insert an APPLICATION pattern: for instance if the
context contain local constants u and f, respectively a sequence and a
function, and if selected object in target is u or f, then it will be
replaced by APP(f, ,?) or APP(u, ?).

Every button has a shortcut, which is either set "manually" or computed
automatically.

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


import logging
from typing import Union

from PySide2.QtCore import Signal, Slot, Qt, QTimer, QSettings
from PySide2.QtGui     import  QKeySequence, QIcon
from PySide2.QtWidgets import (QApplication, QTextEdit, QWidget,
                               QSizePolicy, QScrollArea,
                               QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QToolBar,
                               QAction, QDialog, QDialogButtonBox,
                               QCheckBox,
                               QGroupBox)

import deaduction.pylib.config.dirs as cdirs
from deaduction.pylib.actions import MissingCalculatorOutput

from deaduction.pylib.math_display.nodes import (Node, LogicalNode,
                                                 SetTheoryNode, NumberNode,
                                                 InequalityNode)

from deaduction.pylib.mathobj import MathObject
from deaduction.pylib.pattern_math_obj import (PatternMathObject,
                                               MetaVar)

from deaduction.pylib.marked_pattern_math_object import (MarkedPatternMathObject,
                                                         MarkedMetavar,
                                                         CalculatorPatternLines)

# from deaduction.dui.primitives.base_math_widgets_styling import MathTextWidget
from deaduction.dui.primitives import DisclosureTriangle

from deaduction.dui.stages.calculator.calculator_targets import (
    CalculatorTarget, CalculatorTargets)
from deaduction.dui.stages.calculator.calculator_button import CalculatorButton


global _
log = logging.getLogger(__name__)

if __name__ == "__main__":
    from deaduction.pylib import logger
    logger.configure(domains="deaduction",
                     display_level="debug",
                     filename=None)


Node.PatternMathObject = PatternMathObject
Node.MarkedPatternMathObject = MarkedPatternMathObject


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

        # TODO: implement tooltips for shortcuts
        undo_shortcut = QKeySequence.keyBindings(QKeySequence.Undo)[0].toString()
        redo_shortcut = QKeySequence.keyBindings(QKeySequence.Redo)[0].toString()
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

        self.addAction(self.rewind)
        self.addAction(self.undo_action)
        self.addAction(self.redo_action)
        self.addAction(self.go_to_end)


class NavigationBar(AbstractToolBar):
    """
    A toolbar with navigation buttons: left, right, delete arrows.
    """
    def __init__(self):
        super().__init__()
        # self.setLayoutDirection(Qt.RightToLeft)

        icons_dir = cdirs.icons
        beg_path = str((icons_dir / 'icons8-double-left-48.png').resolve())

        # TODO: implement tooltips for shortcuts
        beginning_shortcut = QKeySequence.keyBindings(
            QKeySequence.MoveToPreviousWord)[0].toString()
        beginning_shortcut = f"({_('type')} {beginning_shortcut})"

        left_shortcut = QKeySequence.keyBindings(
            QKeySequence.MoveToPreviousChar)[0].toString()
        right_shortcut = QKeySequence.keyBindings(
            QKeySequence.MoveToNextChar)[0].toString()
        end_shortcut = QKeySequence.keyBindings(
            QKeySequence.MoveToNextWord)[0].toString()
        delete_shortcut = QKeySequence.keyBindings(
            QKeySequence.Delete)[0].toString()
        self.beginning_action = QAction(QIcon(beg_path),
                                        _('Go to beginning'),
                                        self)

        left_path = str((icons_dir / 'icons8-back-48.png').resolve())
        self.left_action = QAction(QIcon(left_path),
                                   _('Move left'), self)

        # up_path = str((icons_dir /
        #               'icons8-thick-arrow-pointing-up-48.png').resolve())
        # self.up_action = QAction(QIcon(up_path), _('Move up'), self)

        right_path = str((icons_dir / 'icons8-forward-48.png').resolve())
        self.right_action = QAction(QIcon(right_path),
                                   _('Move right'), self)

        end_path = str((icons_dir / 'icons8-double-right-48.png').resolve())
        self.end_action = QAction(QIcon(end_path),
                                   _('Go to end'), self)

        self.delete = QAction(QIcon(str((icons_dir /
                                         'icons8-clear-48.png').resolve())),
                              _('Delete selected block'), self)

        self.addAction(self.beginning_action)
        self.addAction(self.left_action)
        # self.addAction(self.up_action)
        self.addSeparator()
        self.addAction(self.right_action)
        self.addAction(self.end_action)
        self.addAction(self.delete)


class CalculatorButtonsGroup(QWidget):
    """
    A widget to display a list of CalculatorButtons, with a title and a
    disclosure triangle.
    """

    # TODO: API for including new (e.g. context) buttons on the fly.

    col_size = 5

    def __init__(self, title, calculator_buttons: [CalculatorButton],
                 col_size=None, hidden=False):

        super().__init__()
        self.hidden = hidden
        self.title = title
        self.disclosure_triangle = DisclosureTriangle(
            slot=self.toggle_disclosure_triangle, hidden=hidden)
        self.disclosure_triangle.setSizePolicy(QSizePolicy.Fixed,
                                               QSizePolicy.Fixed)
        self.disclosure_triangle.setFocusPolicy(Qt.NoFocus)

        self.group_box = QGroupBox()
        # super().__init__(title)

        if col_size:
            self.col_size = col_size
        self.buttons = []
        self.buttons_layout = QGridLayout()
        for btn in calculator_buttons:
            self.add_button(btn)
        # self.include_buttons()

        self.margin_btns_lyt = QHBoxLayout()
        self.margin_btns_lyt.addStretch()
        self.margin_btns_lyt.addLayout(self.buttons_layout)
        self.margin_btns_lyt.addStretch()

        # Fill-in main layout
        group_box_layout = QVBoxLayout()
        group_box_layout.addLayout(self.margin_btns_lyt)
        self.group_box.setLayout(group_box_layout)

        # main_lyt = QHBoxLayout()
        # main_lyt.addWidget(self.disclosure_triangle)
        # main_lyt.setAlignment(self.disclosure_triangle, Qt.AlignTop)
        # main_lyt.addWidget(self.group_box)
        disclosure_lyt = QHBoxLayout()
        disclosure_lyt.addWidget(self.disclosure_triangle)
        disclosure_lyt.addWidget(QLabel(self.title))
        disclosure_lyt.addStretch()
        disclosure_lyt.setAlignment(Qt.AlignLeft)

        main_lyt = QVBoxLayout()
        main_lyt.addLayout(disclosure_lyt)
        main_lyt.addWidget(self.group_box)
        self.setLayout(main_lyt)

        if self.hidden:
            self.toggle_buttons()

    # def include_buttons(self):
    #     """
    #     Add self's buttons in self.buttons_layout.
    #     """
    #
    #     for line in range(len(self.buttons) // self.col_size + 1):
    #         col = 0
    #         for button in self.buttons[self.col_size * line:
    #                                    self.col_size * (line + 1)]:
    #             self.buttons_layout.addWidget(button, line, col)
    #             col += 1

    def init_btns_lyt(self):
        # TODO: clear lyt
        # self.buttons_layout.removeWidget(w)

        calculator_buttons = self.buttons
        self.buttons = []
        for btn in calculator_buttons:
            self.add_button(btn)

    def add_button(self, button: CalculatorButton):
        line = len(self.buttons) // self.col_size
        col = len(self.buttons) - (line * self.col_size)
        self.buttons_layout.addWidget(button, line, col)
        self.buttons.append(button)

    def remove_button(self, button):
        pass

    def patterns(self):
        """
        List of all patterns from buttons in the group.
        """
        patterns = []
        for button in self.buttons:
            patterns.extend(button.patterns)
        return patterns

    @classmethod
    def from_node_subclass(cls, node_class, col_size=4):
        """
        Construct a CalculatorButtonsGroup from instances of a Node subclass.
        Here node_class should be for instance LogicalNode.
        """
        buttons = [CalculatorButton.from_node(node)
                   for node in node_class.calculator_nodes]
        buttons_group = cls(title=node_class.name(),
                            calculator_buttons=buttons,
                            col_size=col_size)
        return buttons_group

    @classmethod
    def from_calculator_pattern_lines(cls, calc_pattern):
        buttons = []
        # If more than one line, then col_size = length of first line
        col_size = (len(calc_pattern.lines[0]) if len(calc_pattern.lines) > 1
                    else None)
        for line in calc_pattern.lines:
            for symbol in line:
                buttons.append(CalculatorButton(symbol))

        buttons_group = cls(title=calc_pattern.title,
                            calculator_buttons=buttons,
                            col_size=col_size)
        return buttons_group

    @classmethod
    def from_bound_vars(cls, bound_vars):
        title = CalculatorPatternLines.bound_vars_title
        buttons = [CalculatorButton.from_math_object(bound_var)
                   for bound_var in bound_vars]
        btn_group = cls(title=title,
                        calculator_buttons=buttons)
        return btn_group

    def deleteLater(self):
        bad_keys = [key for key, button in CalculatorButton.shortcuts_dic
                    if button in self.buttons]
        for key in bad_keys:
            CalculatorButton.shortcuts_dic.pop(key)
        super().deleteLater()

    def toggle_buttons(self):
        if self.hidden:
            self.group_box.hide()
            for button in self.buttons:
                button.hide()
        else:
            self.group_box.show()
            for button in self.buttons:
                button.show()

    def toggle_disclosure_triangle(self, hidden=None):
        if hidden is None:
            self.hidden = not self.hidden
        else:
            self.hidden = hidden
        self.toggle_buttons()


class CalculatorAllButtons(QWidget):
    """
    A class to display groups of CalculatorButtons, with a vertical scroll bar.
    """

    send_pattern = Signal(MarkedPatternMathObject)
    targets_window: CalculatorTargets = None
    controller = None  # Set by CalculatorController
    # window_closed = Signal()
    targets_window_is_closed = False

    def __init__(self, calc_patterns: [CalculatorPatternLines]):
        super().__init__()
        self.setWindowTitle(_("Math Calculator"))
        # self.setFocusPolicy(Qt.NoFocus)
        self.buttons_groups = []
        # Clear ancient shortcuts!!
        CalculatorButton.shortcuts_dic = {}
        main_lyt = QVBoxLayout()

        ###############
        # Add buttons #
        ###############
        self.btns_wgt = QWidget()
        btns_lyt = QVBoxLayout()

        # Lines from pattern_lines
        for calc_pattern in calc_patterns:
            buttons = CalculatorButtonsGroup.from_calculator_pattern_lines(
                calc_pattern)
            btns_lyt.addWidget(buttons)
            self.buttons_groups.append(buttons)

        # Lines from nodes
        for NodeClass, col_size in ((LogicalNode, 5),
                                    (SetTheoryNode, 5),
                                    (NumberNode, 4),
                                    (InequalityNode, 5)):
            buttons = CalculatorButtonsGroup.from_node_subclass(NodeClass,
                                                                col_size)
            btns_lyt.addWidget(buttons)
            self.buttons_groups.append(buttons)

        btns_lyt.addStretch()
        self.btns_wgt.setLayout(btns_lyt)
        self.btns_scroll_area = QScrollArea()
        self.btns_scroll_area.setWidgetResizable(True)
        # self.btns_scroll_area.setSizePolicy(QSizePolicy.Expanding)
        self.btns_scroll_area.setWidget(self.btns_wgt)

        main_lyt.addWidget(self.btns_scroll_area)
        self.setLayout(main_lyt)

        # Connect button signals
        for btn in self.buttons():
            btn.send_pattern.connect(self.process_clic)

        self.set_geometry()

    def set_geometry(self, geometry=None):
        settings = QSettings("deaduction")
        value = settings.value("calculator/geometry")
        if value:
            self.restoreGeometry(value)
        elif geometry:
            self.setGeometry(geometry)

        for buttons in self.buttons_groups:
            hidden = settings.value(f"calculator/{buttons.title}",
                                     buttons.hidden)
            hidden = (hidden in (True, "true"))
            dt = buttons.disclosure_triangle
            if dt.hidden != hidden:
                buttons.hidden = not hidden
                dt.toggle()
            else:
                buttons.toggle_disclosure_triangle(hidden=hidden)

    def closeEvent(self, event):
        if not self.targets_window_is_closed:
            event.ignore()
        else:
            super().closeEvent(event)

    def close(self):
        # Save window geometry
        settings = QSettings("deaduction")
        settings.setValue("calculator/geometry", self.saveGeometry())

        # Save states of disclosure triangles
        for buttons in self.buttons_groups:
            settings.setValue(f"calculator/{buttons.title}",
                              buttons.hidden)
        super().close()
        print("Buttons wd closed!")
        # self.window_closed.emit()

    def buttons(self) -> [CalculatorButton]:
        btns = []
        for buttons_group in self.buttons_groups:
            btns.extend(buttons_group.buttons)
        return btns

    @Slot()
    def process_clic(self, pattern):
        self.send_pattern.emit(pattern)


class CalculatorMainWindow(QDialog):
    """
    A class to display a "calculator", i.e. a QWidget that enables usr to
    build a new MathObject (a new mathematical object or property).
    """

    send_pattern = Signal(MarkedPatternMathObject)

    def __init__(self, calc_patterns: [CalculatorPatternLines]):
        super().__init__()

        # self.key_event_buffer = ""

        self.toolbar = CalculatorToolbar()
        self.navigation_bar = NavigationBar()

        main_lyt = QVBoxLayout()
        main_lyt.addWidget(self.toolbar)

        self.buttons_groups = []
        # Clear ancient shortcuts!!
        CalculatorButton.shortcuts_dic = {}

        ###############
        # Add buttons #
        ###############
        self.btns_wgt = QWidget()
        btns_lyt = QVBoxLayout()

        # Lines from pattern_lines
        for calc_pattern in calc_patterns:
            buttons = CalculatorButtonsGroup.from_calculator_pattern_lines(
                calc_pattern)
            btns_lyt.addWidget(buttons)
            self.buttons_groups.append(buttons)

        # Lines from nodes
        for NodeClass, col_size in ((LogicalNode, 5),
                                    (SetTheoryNode, 5),
                                    (NumberNode, 4),
                                    (InequalityNode, 5)):
            buttons = CalculatorButtonsGroup.from_node_subclass(NodeClass,
                                                                col_size)
            btns_lyt.addWidget(buttons)
            self.buttons_groups.append(buttons)

        btns_lyt.addStretch()
        self.btns_wgt.setLayout(btns_lyt)
        self.btns_scroll_area = QScrollArea()
        self.btns_scroll_area.setWidgetResizable(True)
        # self.btns_scroll_area.setSizePolicy(QSizePolicy.Expanding)
        self.btns_scroll_area.setWidget(self.btns_wgt)

        main_lyt.addWidget(self.btns_scroll_area)

        # Connect button signals
        for btn in self.buttons():
            btn.send_pattern.connect(self.process_clic)

        # main_lyt.addStretch()

        ####################
        # CalculatorTarget #
        ####################
        # calculator_target will process key events and send them to the
        # toolbars
        self.calculator_target = CalculatorTarget()
        self.calculator_target_title = QLabel()
        self.calculator_target_title.setStyleSheet("font-weight: bold; ")
        main_lyt.addWidget(self.calculator_target_title)
        main_lyt.addWidget(self.calculator_target)

        ###################
        # Navigation btns #
        ###################
        # main_lyt.addWidget(self.navigation_bar)
        nav_lyt = QHBoxLayout()
        nav_lyt.addWidget(self.navigation_bar)
        nav_lyt.addStretch()
        self.lean_mode_wdg = QCheckBox("Lean mode")
        self.lean_mode_wdg.setFocusPolicy(Qt.NoFocus)
        nav_lyt.addWidget(self.lean_mode_wdg)

        main_lyt.addLayout(nav_lyt)

        ####################
        # OK / Cancel btns #
        ####################
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok)
                                           # | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.close_n_accept)
        main_lyt.addWidget(self.button_box)
        self.setLayout(main_lyt)

        # Connect calculator_target
        self.calculator_target.navigation_bar = self.navigation_bar
        self.calculator_target.toolbar = self.toolbar
        self.calculator_target.button_box = self.button_box
        self.calculator_target.setFocus()

        self.set_geometry()

    def set_geometry(self, geometry=None):
        settings = QSettings("deaduction")
        value = settings.value("calculator/geometry")
        if value:
            self.restoreGeometry(value)
        elif geometry:
            self.setGeometry(geometry)

        for buttons in self.buttons_groups:
            hidden = settings.value(f"calculator/{buttons.title}",
                                     buttons.hidden)
            hidden = (hidden in (True, "true"))
            dt = buttons.disclosure_triangle
            if dt.hidden != hidden:
                buttons.hidden = not hidden
                dt.toggle()
            else:
                buttons.toggle_disclosure_triangle(hidden=hidden)

    def close(self):
        # Save window geometry
        settings = QSettings("deaduction")
        settings.setValue("calculator/geometry", self.saveGeometry())

        # Save states of disclosure triangles
        for buttons in self.buttons_groups:
            settings.setValue(f"calculator/{buttons.title}",
                              buttons.hidden)

    def close_n_accept(self):
        self.close()
        self.accept()

    def reject(self):
        self.close()
        super().reject()

    def set_target_title(self, title):
        self.calculator_target_title.setText(title)

    def buttons(self) -> [CalculatorButton]:
        btns = []
        for buttons_group in self.buttons_groups:
            btns.extend(buttons_group.buttons)
        return btns

    # def add_bound_var_btn(self):

    def set_html(self, text):
        self.calculator_target.setHtml(text)

    @Slot()
    def process_clic(self, pattern):
        self.send_pattern.emit(pattern)

    def bound_var_group(self):
        for group in self.buttons_groups:
            if group.title == CalculatorPatternLines.bound_vars_title:
                return group


class CalculatorController:
    """
    The calculator controller. This is initiated with
    - a MarkedPatternMathObject, typically just a Metavar, that stands for
    the object under construction.
    - a dictionary of CalculatorGroup instances, that is used to build the
    various buttons groups. This is in general empty, since buttons are
    automatically generated:
        - context and definition buttons, in __init__()
        - standard buttons, in CalculatorMainWindow.

    Note that the targets are entirely managed from the CalculatorController,
    and not at the CalculatorTargets level.
    """

    _target: MarkedPatternMathObject
    targets_window: CalculatorTargets

    ################
    # init methods #
    ################

    def __init__(self, target_type=None,
                 goal=None,
                 calculator_groups=None,
                 window_title="Math Calculator",
                 task_title=None,
                 target_types=None,
                 titles=None,
                 # task_description=None,
                 task_goal=None,
                 prop=None):

        self.goal = goal
        self.targets = []
        self.target_types = target_types if target_types else None
        nb = self.nb_of_targets
        # One history empty list per target, but they must be distinct lists!
        self.histories: [[MarkedPatternMathObject]] = []
        for idx in range(nb):
            self.histories.append([])
        # First target history will be updated immediately (so set at -1)
        self.history_indices = [0] * nb

        if target_types:
            # self.window_title = window_title
            # self.task_title = task_title
            self.target_types = target_types
            # self.titles = titles
            # self.task_description = task_description

            targets_window = CalculatorTargets(window_title=window_title,
                                               target_types=target_types,
                                               titles=titles,
                                               task_title=task_title,
                                               # task_description=task_description,
                                               task_goal=task_goal,
                                               prop=prop)
            self.targets_window = targets_window
            # wdg_classes = [CalculatorAllButtons,
            #                CalculatorButtonsGroup,
            #                CalculatorButton,
            #                DisclosureTriangle,
            #                CalculatorTargets]
            # self.targets_window.steal_focus_from_list.extend(wdg_classes)
            focus_changed = QApplication.instance().focusChanged
            focus_changed.connect(targets_window.on_focus_changed)
            focus_has_changed = targets_window.focus_has_changed
            focus_has_changed.connect(self.target_focus_has_changed)
            self.targets_window.window_closed.connect(
                self.targets_window_closed)

        else:
            # self.task_description = None
            self.targets_window = None

            ##############
            # Set target #
            ##############
            self.targets_window: CalculatorTargets = None
            if not target_type:
                target_type = MetaVar()
                p_target_type = MarkedPatternMathObject.from_pattern_math_object(
                    target_type)
                self.target_title = _("Build your object")
            else:
                p_target_type = MarkedPatternMathObject.from_math_object(target_type)
                display_type = target_type.math_type_to_display(format_="utf8",
                                                                is_math_type=True,
                                                                text=True)
                if target_type.is_prop(is_math_type=True):  # Fixme?
                    display_type = _('a property')
                self.target_title = _("Enter") + " " + display_type + _(":")

            target_mvar = MetaVar(math_type=p_target_type)
            self.targets = [MarkedMetavar.from_mvar(target_mvar)]
            self.targets[0].mark()

        ###########
        # Buttons #
        ###########
        self.calculator_groups = []

        # Context buttons #
        if goal:
            context = goal.context_objects
            context_line = CalculatorPatternLines.from_context(context)
            # bound_vars = CalculatorPatternLines.bound_vars()
            # self.calculator_groups.extend([context_line, bound_vars])
            self.calculator_groups.extend([context_line])
            # Compute applications on ContextMathObjects:
            MarkedPatternMathObject.populate_applications_from_context(context)

        if calculator_groups:
            self.calculator_groups.extend(calculator_groups)
        # Add 'constant' from definitions,
        # e.g. is_bounded, is_even, and so on

        # Definition buttons #
        cpls = CalculatorPatternLines.constants_from_definitions()
        self.calculator_groups.extend(cpls)

        # User interface #
        if self.target_types:
            self.buttons_window = CalculatorAllButtons(self.calculator_groups)
            # self.buttons_window.setParent(self.targets_window)
            # --> buttons_window does not show!
            # self.buttons_window.setFocusProxy(self.targets_window)
            #  --> click on buttons has no effect
            self.buttons_window.controller = self  # Useless?
            self.__set_targets()
            self.__init_multiple_signals()
            self.buttons_window.send_pattern.connect(self.insert_pattern)
        else:
            self.calculator_ui = CalculatorMainWindow(self.calculator_groups)
            self.calculator_ui.setWindowTitle(window_title)
            self.calculator_ui.set_target_title(self.target_title)
            # self.calculator_ui.set_target(target)
            self.calculator_ui.send_pattern.connect(self.insert_pattern)

            self.__init_signals()

        self.__init_histories()
        self.__init_targets()
        self.set_target_and_update_ui()

    @classmethod
    def get_item(cls, goal, target_type, title) -> (Union[PatternMathObject,
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
        calculator_controller = cls(goal=goal,
                                    target_type=target_type,
                                    window_title=title)
        # Execute the ButtonsDialog and wait for results
        OK = calculator_controller.calculator_ui.exec()

        # After exec
        choice = calculator_controller.target
        choice.unmark()

        if calculator_controller.lean_mode:
            choice = calculator_controller.current_target.toPlainText()
            math_object = MathObject(node="RAW_LEAN_CODE",
                                     info={'name': '(' + choice + ')'},
                                     children=[],
                                     math_type=None)
        else:
            # choice = MarkedPatternMathObject.generic_parentheses(choice.assigned_math_object)
            math_object = choice.assigned_math_object

        return math_object, OK

    @classmethod
    def get_items(cls, goal=None,
                  missing_output: MissingCalculatorOutput = None)->\
                                                        ([MathObject], bool):
        """
        Get one or several targets.
        """
        window_title = missing_output.title
        task_title = missing_output.task_title()
        target_types, titles = missing_output.targets_types_n_titles()
        # task_description = missing_output.task_description()
        statement = missing_output.statement
        task_goal = statement.goal() if statement else None
        prop = missing_output.explicit_math_type_of_prop()

        log.debug(f"Calculator with target types")
        calculator_controller = cls(goal=goal,
                                    window_title=window_title,
                                    task_title=task_title,
                                    target_types=target_types,
                                    titles=titles,
                                    # task_description=task_description,
                                    task_goal=task_goal,
                                    prop=prop)
        # Execute the ButtonsDialog and wait for results
        calculator_controller.buttons_window.show()
        OK = calculator_controller.targets_window.exec()

        if not OK:
            calculator_controller.targets_window_closed()
            return [], OK
        ############################
        # After exec: post-process #
        ############################
        targets = calculator_controller.targets
        math_objects = []

        for target in targets:
            target.unmark()
            if not target.assigned_math_object:
                # No more data from this point
                # math_object = MathObject.place_holder()
                break
            elif calculator_controller.lean_mode:
                target = target.toPlainText()
                math_object = MathObject(node="RAW_LEAN_CODE",
                                         info={'name': '(' + target + ')'},
                                         children=[],
                                         math_type=None)
            else:
                # choice = MarkedPatternMathObject.generic_parentheses(choice.assigned_math_object)
                math_object = target.assigned_math_object
            math_objects.append(math_object)

        # while len(targets) > 0 and targets[-1].is_place_holder():
        #     targets.pop()

        math_objects = missing_output.initial_place_holders + math_objects
        return math_objects, OK

    def __set_targets(self):
        """
        Fill-in self.targets with MarkedMetavar whose target types are taken
        in self.target_types.
        """
        self.targets = []
        idx = 0
        for target_type in self.target_types:
            if target_type:
                target_mvar = MetaVar(math_type=target_type)
            else:
                target_mvar = MetaVar(math_type=None)
            target = MarkedMetavar.from_mvar(target_mvar)
            target.mark()
            text = target.to_display(format_='html')
            self.targets_window.target_wdgs[idx].setHtml(text)
            self.targets.append(target)
            idx += 1

    def __init_multiple_signals(self):
        # self.buttons_window.targets_window = self.targets_window
        buttons_window = self.buttons_window
        targets_window = self.targets_window

        t_bar = targets_window.toolbar
        t_bar.rewind.triggered.connect(self.history_to_beginning)
        t_bar.undo_action.triggered.connect(self.history_undo)
        t_bar.redo_action.triggered.connect(self.history_redo)
        t_bar.go_to_end.triggered.connect(self.history_to_end)

        n_bar = targets_window.navigation_bar
        n_bar.beginning_action.triggered.connect(self.go_to_beginning)
        n_bar.left_action.triggered.connect(self.move_left)
        # n_bar.up_action.triggered.connect(self.move_up)
        n_bar.right_action.triggered.connect(self.move_right)
        n_bar.end_action.triggered.connect(self.go_to_end)
        targets_window.lean_mode_wdg.stateChanged.connect(self.set_lean_mode)
        n_bar.delete.triggered.connect(self.delete)

    def __init_signals(self):
        calc_ui = self.calculator_ui

        t_bar = calc_ui.toolbar
        t_bar.rewind.triggered.connect(self.history_to_beginning)
        t_bar.undo_action.triggered.connect(self.history_undo)
        t_bar.redo_action.triggered.connect(self.history_redo)
        t_bar.go_to_end.triggered.connect(self.history_to_end)

        n_bar = calc_ui.navigation_bar
        n_bar.beginning_action.triggered.connect(self.go_to_beginning)
        n_bar.left_action.triggered.connect(self.move_left)
        # n_bar.up_action.triggered.connect(self.move_up)
        n_bar.right_action.triggered.connect(self.move_right)
        n_bar.end_action.triggered.connect(self.go_to_end)
        calc_ui.lean_mode_wdg.stateChanged.connect(self.set_lean_mode)
        n_bar.delete.triggered.connect(self.delete)

    def __init_histories(self):
        for target, history in zip(self.targets, self.histories):
            history.append(target)

    def __init_targets(self):
        if self.targets_window:
            idx = 0
            for target, target_wdg in zip(self.targets,
                                          self.targets_window.target_wdgs):
                target.set_math_cursor()
                target.math_cursor.go_to_end()
                target_wdg.setHtml(target.to_display(format_='html'))
                self.targets_window.set_focused_target_idx(idx)
                self.update_cursor()
                idx += 1

            self.targets_window.set_focused_target_idx(0)

    def show(self):
        if self.target_types:
            self.targets_window.show()
        else:
            self.calculator_ui.show()

    def targets_window_closed(self):
        print("Targets wd closed")
        self.buttons_window.targets_window_is_closed = True
        self.buttons_window.close()

    @property
    def nb_of_targets(self):
        if self.target_types:
            return len(self.target_types)
        else:
            return 1

    @property
    def current_target_idx(self):

        idx = (self.targets_window.focused_target_idx if self.targets_window
               else 0)
        return idx

    @property
    def history(self) -> []:
        return self.histories[self.current_target_idx]

    @history.setter
    def history(self, old_target) -> []:
        self.histories[self.current_target_idx] = old_target

    @property
    def history_idx(self):
        return self.history_indices[self.current_target_idx]

    @history_idx.setter
    def history_idx(self, idx):
        self.history_indices[self.current_target_idx] = idx

    @property
    def current_target_wdg(self):
        if self.targets_window:
            calc_target = self.targets_window.focused_target
        else:
            calc_target = self.calculator_ui.calculator_target
        return calc_target

    @property
    def current_target(self):
        return self.targets[self.current_target_idx]

    @property
    def target(self):
        return self.current_target

    # @property
    # def target(self):
    #     return self._target
    #

    @target.setter
    def target(self, target):
        """
        Set current target.
        """
        self.targets[self.current_target_idx] = target

    @property
    def math_cursor(self):
        if self.target:
            return self.target.math_cursor

    @Slot()
    def set_lean_mode(self):
        self.current_target_wdg.lean_mode = self.lean_mode
        if self.lean_mode:
            self.set_target()
        else:
            self.set_target_and_update_ui()

    @property
    def lean_mode(self) -> bool:
        mode = self.lean_mode_wdg.isChecked()
        return mode

    @property
    def html_target(self):
        if self.lean_mode:
            text = self.target.to_display(format_='lean')
        else:
            text = self.target.to_display(format_='html')
        return text

    @property
    def current_html_target(self):
        if self.lean_mode:
            text = self.current_target.to_display(format_='lean')
        else:
            text = self.current_target.to_display(format_='html')
        return text

    @property
    def navigation_bar(self):
        if self.targets_window:
            bar = self.targets_window.navigation_bar
        else:
            bar = self.calculator_ui.navigation_bar
        return bar

    @property
    def toolbar(self):
        if self.targets_window:
            bar = self.targets_window.toolbar
        else:
            bar = self.calculator_ui.toolbar
        return bar

    @property
    def lean_mode_wdg(self):
        return (self.targets_window.lean_mode_wdg if self.targets_window else
                self.calculator_ui.lean_mode_wdg)

    @property
    def beginning_action(self):
        return self.navigation_bar.beginning_action

    @property
    def left_action(self):
        return self.navigation_bar.left_action

    @property
    def right_action(self):
        return self.navigation_bar.right_action

    @property
    def end_action(self):
        return self.navigation_bar.end_action

    @property
    def undo_action(self):
        return self.toolbar.undo_action

    @property
    def redo_action(self):
        return self.toolbar.redo_action

    @Slot()
    def set_target(self):
        self.current_target_wdg.setHtml(self.html_target)
        # self.calculator_ui.set_html(self.html_target)

    def virtual_cursor_position(self):
        """
        Return the position at which the cursor should be seen, corresponding to
        the current marked node of self.target, if any, or the end.
        """
        return self.math_cursor.linear_text_cursor_position()

    def update_cursor(self):
        # self.target.adjust_cursor_pos()
        # self.calculator_ui.calculator_target.setFocus()
        position = self.virtual_cursor_position()
        self.current_target_wdg.go_to_position(position)

    def enable_actions(self):
        # target = self.target
        cursor = self.math_cursor
        self.beginning_action.setEnabled(not cursor.is_at_beginning())
        # self.left_unassigned_action.setEnabled(bool(target.previous_unassigned()))
        self.left_action.setEnabled(not cursor.is_at_beginning())
        # self.up_action.setEnabled(bool(target.parent_of_marked()))
        self.right_action.setEnabled(not cursor.is_at_end())
        # self.right_unassigned_action.setEnabled(bool(target.next_unassigned()))
        self.end_action.setEnabled(not cursor.is_at_end())
        self.undo_action.setEnabled(self.history_idx > 0)
        self.redo_action.setEnabled(self.history_idx < len(self.history) - 1)

        # Has usr filled-in enough targets?
        #  All place_holders must be at the end,
        #  i.e. no assigned_math_object after unassigned
        assigned_math_objects = [var.assigned_math_object
                                 for var in self.targets]
        place_holders_found = False
        OK = False
        for mo in assigned_math_objects:
            if mo is None:
                if not OK:  # No initial assigned_math_object
                    break
                else:
                    place_holders_found = True
            elif mo is not None and place_holders_found:
                OK = False
                break
            else:  # At least one assigned_math_object
                OK = True
        button_box = (self.targets_window.button_box if self.targets_window
                      else self.calculator_ui.button_box)
        button_box.setEnabled(OK)

    @Slot()
    def target_focus_has_changed(self):
        self.enable_actions()

    # def update_cursor_and_enable_actions(self):
    #     self.update_cursor()
    #     self.enable_actions()
    #     self.current_target_wdg.setFocus()
    #     # print(self.target)

    def give_focus_back_to_target_wdg(self):
        """
        Give focus back to targets_window (and thus to the active
        target_wdg). This prevents the Buttons window to keep focus.
        """
        if self.targets_window:
            self.targets_window.activateWindow()
            self.targets_window.setFocus()

    def set_target_and_update_ui(self):
        self.set_target()
        # self.update_bound_vars()
        self.update_cursor()
        self.enable_actions()
        self.give_focus_back_to_target_wdg()

    ##################
    # Target editing #
    ##################

    def history_update(self):
        """
        Update target display, and store it in history.
        Delete the end of history if any.
        This is called after insert_pattern() and delete() methods.
        """

        self.history_idx += 1
        self.history = self.history[:self.history_idx]
        self.history.append(self.target)
        self.set_target_and_update_ui()

    # def bound_var_buttons_group(self):
    #     bv_group = self.calculator_ui.bound_var_group()
    #     return bv_group
    #
    # def bound_vars_from_buttons(self):
    #     bound_vars = self.bound_var_buttons_group().patterns()
    #     return bound_vars
    #
    # def check_new_bound_var(self, assigned_mvar):
    #     """
    #     If assigned_mvar affected the type of some bound var, then
    #     rename this bound var. FIXME: no bound vars in Calculator.
    #     """
    #
    #     bv_group = self.calculator_ui.bound_var_group()
    #
    #     # (0) Record new bound vars
    #     if assigned_mvar.has_bound_var():
    #         new_bound_var = assigned_mvar.bound_var
    #         self.bound_vars.append(new_bound_var)
    #         button = CalculatorButton.from_math_object(new_bound_var)
    #         bv_group.add_button(button)
    #         button.send_pattern.connect(self.calculator_ui.process_clic)
    #
    #     # (1) Name bound vars that have just been given a type
    #     target = self.target
    #     bound_var = target.bound_var_affected_by(assigned_mvar)
    #     if bound_var:
    #         # (1a) Name bound_var
    #         bound_var.is_unnamed = True
    #         self.goal.name_one_bound_var(bound_var)  # FIXME, bad names
    #         # Propagate name in target.bound_vars()
    #         # FIXME: should be useless(
    #
    #         for bv in target.bound_vars():
    #             if bound_var.refer_to_the_same_bound_var(bv):
    #                 if bv.name != bound_var.name:
    #                     # FIXME: does not work
    #                     bv.set_unnamed_bound_var()
    #                     bv.name_bound_var(bound_var.name)
    #
    #         # (1b) Propagate name in self.bound_vars fixme: useless??
    #         for bv in self.bound_vars:
    #             if bound_var.refer_to_the_same_bound_var(bv):
    #                 bv.set_unnamed_bound_var()
    #                 bv.name_bound_var(bound_var.name)
    #         # (1c) And change buttons accordingly
    #         for button in bv_group.buttons:
    #             button_bv = button.patterns[0]
    #             button.reset_text(button_bv.name)
    #
    # def update_bound_vars(self, previous_bound_vars, new_bound_vars):
    #     """
    #     Compare self.bound_vars() and self.target.bound_vars(),
    #     create or delete or modify buttons accordingly.
    #     """
    #     # FIXME
    #
    #     target = self.target
    #     bv_group = self.calculator_ui.bound_var_group()
    #
    #     set_of_bv1 = set([bv.info.get('identifier_nb')
    #                       for bv in self.bound_vars
    #                       if bv.info.get('identifier_nb')])
    #     set_of_bv2 = set([bv.info.get('identifier_nb')
    #                       for bv in target.bound_vars()
    #                       if bv.info.get('identifier_nb')])
    #     target_ident = [bv.info.get('identifier_nb')
    #                       for bv in target.bound_vars()]
    #     to_be_removed = []
    #     for bv in self.bound_vars:
    #         ident = bv.info.get('identifier_nb')
    #         if ident not in target_ident:
    #             to_be_removed.append(bv)
    #
    #     if to_be_removed:
    #         for bv in to_be_removed:
    #             self.bound_vars.remove(bv)
    #         new_group = CalculatorButtonsGroup.from_bound_vars(self.bound_vars)
    #         ui_lyt = self.calculator_ui.btns_wgt.layout()
    #         # ui_lyt.replaceWidget(bv_group, new_group)
    #         # bv_group.deleteLater()
    #         idx = ui_lyt.indexOf(bv_group)
    #         print(f"Idx of bv group: {idx}")
    #         ui_lyt.removeWidget(bv_group)
    #         bv_group.hide()
    #         ui_lyt.insertWidget(idx, new_group)

    @Slot()
    def insert_pattern(self, pattern_s: [MarkedPatternMathObject]):
        """
        Try to insert pattern (or patterns) in self.target.
        If several patterns are provided, they are tried in order until
        success.

        The case of the special pattern "GENERIC_APPLICATION" is different.
        This is called when usr push the "()" button, or the "f(·)" button.
        If the marked_descendant is a function g from the context, then the
        insertion will result in the object g(·). This is done by computing
        beforehand the pattern APP(g, ?) for every context function g.
        """

        new_target = self.target.deep_copy(self.target)
        # Do not affect marked_descendant:
        new_target.set_math_cursor(go_to_end=False)
        new_target.math_cursor.set_cursor_at_the_same_position_as(
            self.target.math_cursor)
        assert (new_target.math_cursor.cursor_address ==
                self.target.math_cursor.cursor_address)
        assert (new_target.math_cursor.cursor_is_after ==
                self.target.math_cursor.cursor_is_after)
        # print("Target, new target ordered descendants:")
        # print(self.target.ordered_descendants(include_cursor=True))
        # print(new_target.ordered_descendants(include_cursor=True))

        assigned_mvar = None
        print(f"New target: {new_target}")

        if not isinstance(pattern_s, list):
            pattern_s = [pattern_s]

        # (1) Normal insert
        for pattern in pattern_s:
            if pattern.node == "GENERIC_APPLICATION":  # FIXME: obsolete?
                # (1a) Special buttons: applications
                # g --> g(·)
                assigned_mvar = new_target.insert_application()
            else:
                # (1b) Normal insert
                assigned_mvar = new_target.insert(pattern)
                # assigned_mvar = new_target.new_insert(pattern)
            if assigned_mvar:
                break

        pattern = pattern_s[-1]
        # (2) Automatic patterns
        # g, x --> g(x)  ; u, n --> u_n
        if not assigned_mvar:
            assigned_mvar = new_target.insert_application_with_arg(pattern)

        # (3) Force insertion with LAST pattern
        # FOr now this just fusions digits
        #  1, 2 --> 12
        if not assigned_mvar:
            assigned_mvar = new_target.generic_insert(pattern)

        # print(f"New target: {new_target}")
        if assigned_mvar:
            assigned_mvar.adjust_type_of_assigned_math_object()
            self.target = new_target
            # self.check_new_bound_var(assigned_mvar)
            was_at_end = (self.target.math_cursor.is_at_end()
                          or self.target.marked_descendant() ==
                          self.target.ordered_descendants()[-1])
            self.target.move_after_insert(assigned_mvar,
                                          was_at_end=was_at_end)
            self.history_update()
        else:
            # Fixme
            self.current_target_wdg.setFocus()
        # print(f"Shape: {self.target.latex_shape()}")
        # print(f"New target after move: {new_target}")
        # print("Math list:")
        # self.math_cursor.show_cursor()
        # print(self.target.math_list())
        # self.math_cursor.hide_cursor()
        # print("Linear list, idx:")
        # print(self.target.ordered_descendants())
        # print(self.target.current_index_in_ordered_descendants())
        # total, cursor = self.target.total_and_cursor_list()
        # print("Total and cursor lists:")
        # print(total)
        # print(cursor)
        # print("Bound vars:")
        # BV = self.target.bound_vars()
        # print(BV)
        # print([bv.info.get('identifier_nb') for bv in BV])
        # print(self.target.math_type)

    @Slot()
    def delete(self):
        new_target = self.target.deep_copy(self.target)
        # FIXME: record element previous to marked, and go_to that element
        #  after deletion
        success = new_target.clear_marked_mvar()
        # print(new_target)
        if success:
            self.target = new_target
            self.history_update()

    #################
    # History moves #
    #################

    def after_history_move(self):
        """
        Update after a history move.
        """
        self.target = self.history[self.history_idx]
        self.set_target_and_update_ui()
        # TODO: enable/disable buttons

    @Slot()
    def history_undo(self):
        if self.history_idx > 0:
            self.history_idx -= 1
            self.after_history_move()

    @Slot()
    def history_redo(self):
        if self.history_idx < len(self.history) - 1:
            self.history_idx += 1
            self.after_history_move()

    @Slot()
    def history_to_beginning(self):
        self.history_idx = 0
        self.after_history_move()

    @Slot()
    def history_to_end(self):
        self.history_idx = len(self.history) - 1
        self.after_history_move()

    ################
    # Cursor moves #
    ################

    @Slot()
    def move_right(self):
        self.math_cursor.increase_pos()
        self.set_target_and_update_ui()

    @Slot()
    def move_left(self):
        self.math_cursor.decrease_pos()
        self.set_target_and_update_ui()

    @Slot()
    def go_to_beginning(self):
        self.math_cursor.go_to_beginning()
        self.set_target_and_update_ui()

    @Slot()
    def go_to_end(self):
        self.math_cursor.go_to_end()
        self.set_target_and_update_ui()

    @Slot()
    def move_to_next_unassigned(self):
        success = self.target.move_right_to_next_unassigned()
        if success:
            self.calculator_ui.set_html(self.html_target)
            self.set_target_and_update_ui()

    @Slot()
    def move_to_previous_unassigned(self):
        success = self.target.move_left_to_previous_unassigned()
        if success:
            self.set_target_and_update_ui()

    # @Slot()
    # def move_up(self):
    #     success = self.target.move_up()
    #     if success:
    #         self.set_target_and_update()


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
    choice, ok = CalculatorController.get_item(goal=None,
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






