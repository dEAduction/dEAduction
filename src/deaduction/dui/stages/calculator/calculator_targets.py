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
import logging

from PySide2.QtCore import Signal, Slot, Qt, QTimer, QSettings
from PySide2.QtGui     import  QKeySequence, QIcon
from PySide2.QtWidgets import (QTextEdit, QWidget,
                               QSizePolicy, QScrollArea,
                               QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QToolBar,
                               QAction, QDialog, QDialogButtonBox,
                               QCheckBox,
                               QGroupBox)

import deaduction.pylib.config.dirs as cdirs
from deaduction.dui.primitives.base_math_widgets_styling import (
    MathTextWidget, MathLabel)
from deaduction.dui.elements import GoalWidget
from deaduction.dui.stages.calculator.calculator_button import CalculatorButton

log = logging.getLogger(__name__)
global _


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
        self.undo_all = QAction(QIcon(str((icons_dir /
                                    'goback-begining.png').resolve())),
                _('Undo all'), self)
        self.undo_action = QAction(QIcon(str((icons_dir /
                                         'undo_action.png').resolve())),
                _('Undo'), self)
        self.redo_action = QAction(QIcon(str((icons_dir /
                                         'redo_action.png').resolve())),
                _('Redo'), self)
        self.redo_all = QAction(QIcon(str((icons_dir /
                                            'go-end-96.png').resolve())),
                _('Redo all'), self)

        self.addAction(self.undo_all)
        self.addAction(self.undo_action)
        self.addAction(self.redo_action)
        self.addAction(self.redo_all)


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


class CalculatorTarget(MathTextWidget):
    """
    This is the class for the Calculator "target", whose purpose is to
    display the MathObject (or more precisely, MarkedPatternMathObject) that
    usr is building. Note that the text from kbd is not processed by the
    super class QTextEdit, unless Calculator is in Lean mode. Instead,
    kbd events are intercepted and serve as shortcuts from buttons. All input
    come from the buttons.
    """

    key_event_item_interval = 1000

    def __init__(self):
        super().__init__()

        # Double default cursor width
        self.setCursorWidth(self.cursorWidth()*2)

        self.set_selection(True)

        self.setFixedHeight(50)  # fixme
        # self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.NoWrap)
        # self.setLineWrapColumnOrWidth(10000)

        self.navigation_bar = None
        self.toolbar = None
        self.button_box = None

        # Set key_event_buffer and timer
        self.key_event_buffer = ""
        self.key_buffer_timer = QTimer()
        self.key_buffer_timer.setInterval(self.key_event_item_interval)
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

        self.key_buffer_timer.start()

        key = event.key()
        if int(event.modifiers()) & int(Qt.ControlModifier):
            # print("CTRL")
            key += Qt.CTRL
            # print(key_sqc)
            # print(key_sqc == QKeySequence.Undo)
        if int(event.modifiers()) & int(Qt.ShiftModifier):
            # print("SHIFT")
            key += Qt.SHIFT
        if int(event.modifiers()) & int(Qt.AltModifier):
            # print("ALT")
            key += Qt.ALT
        if int(event.modifiers()) & int(Qt.MetaModifier):
            # print("META")
            key += Qt.META

        key_sequence = QKeySequence(key)
        # print(key_sequence == QKeySequence.Undo)
        # log.debug("Key event -> Trying Return and Space")
        if key_sequence == QKeySequence("Return"):
            self.button_box.button(QDialogButtonBox.Ok).animateClick()
        elif key_sequence == QKeySequence("Space"):
            self.key_buffer_timeout()
            event.ignore()
            return

        # QAction key sequences
        action = None
        bar = None
        # Navigation
        # log.debug("Key event -> Trying nav")
        if key_sequence == QKeySequence.MoveToPreviousWord:
            bar = self.navigation_bar
            action = bar.beginning_action
        elif key_sequence == QKeySequence.MoveToPreviousChar:
            print("<-")
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
        if self.key_buffer_timer.isActive():
            self.key_buffer_timer.stop()

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


class CalculatorTargets(QDialog):
    """
    This class displays one or several CalculatorTarget,
    with a title, a math property and individual titles.
    The math property is given either as a Goal instance (.e.g. applying a
    Statement) or as a MathObject instance (e.g. applying a context property).
    e.g.:
    (1) A single target:
        title = Define a new sub-goal
        No task_description
        --> Target with type = Prop

    (2) Several targets:
        title = Apply the following theorem/property:
        task_description = forall X, Y, Z, forall f:X -> Y, forall g: Y -> Z,
        f continuous and g continuous ==> g circ f continuous.

        --> Targets corresponding to f and g, with titles
                "Which object plays the role of f?"
                "Which object plays the role of g?"

    It also displays a toolbar with history moves, and a navigation bar.
    When self has the focus, focus is transferred to the focused_target.
    """

    focus_has_changed = Signal()
    window_closed = Signal()

    titles_font_size = 15

    steal_focus_from_list = []

    def __init__(self, window_title,
                 target_types: [],  # MathObject
                 titles: [str],
                 task_title=None,
                 # task_description=None,
                 task_goal=None,
                 prop=None):
        """        
        @param task_description: either a goal, a MathObject or a string.
        @param target_types: a list of MathObjects.
        @param titles: a list of strings.
        """

        assert target_types
        if len(titles) < len(target_types):
            titles += [None]*(len(target_types) - len(titles))

        super().__init__()
        self.setWindowTitle(window_title + " — d∃∀duction")
        self.setWindowModality(Qt.WindowModal)
        # self.setWindowModality(Qt.NonModal)

        # Toolbar
        self.toolbar = CalculatorToolbar()

        ####################
        # Detailed context #
        ####################
        self.task_title_widget = None
        self.task_widget = None
        fs = self.titles_font_size
        if task_goal:
            self.task_title_widget = QLabel(task_title)
            self.task_title_widget.setStyleSheet("font-weight: bold; "
                                                 f"font-size: {fs}pt")

            self.task_widget = GoalWidget(goal=task_goal,
                                          open_problem=False,
                                          to_prove=False)
        elif prop:
            self.task_title_widget = QLabel(task_title)
            self.task_title_widget.setStyleSheet("font-weight: bold; "
                                                 f"font-size: {fs}pt")

            self.task_widget = GoalWidget(math_object=prop,
                                          open_problem=False,
                                          to_prove=False)
        elif task_title:
            self.task_title_widget = QLabel(task_title)
            self.task_title_widget.setStyleSheet("font-weight: bold; "
                                                 f"font-size: {fs}pt")
        # elif task_description:
        #     if not isinstance(task_description, str):
        #         task_description = task_description.to_display(format_='html')
        #
        #     self.task_widget = QGroupBox()
        #     self.task_widget.setTitle(task_title)
        #     math_lbl = MathLabel()
        #     math_lbl.setText(task_description)
        #     lyt = QHBoxLayout()
        #     lyt.addWidget(math_lbl)
        #     self.task_widget.setLayout(lyt)
        # else:
        #     self.task_widget = None

        ######################
        # Navigation buttons #
        ######################
        self.navigation_bar = NavigationBar()
        self.lean_mode_wdg = QCheckBox("Lean mode")
        self.lean_mode_wdg.setFocusPolicy(Qt.NoFocus)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        self.button_box.accepted.connect(self.close_n_accept)
        nav_lyt = QHBoxLayout()
        nav_lyt.addWidget(self.navigation_bar)
        nav_lyt.addStretch()
        nav_lyt.addWidget(self.lean_mode_wdg)
        nav_lyt.addWidget(self.button_box)

        ###########
        # Targets #
        ###########
        title_wdgs = []
        self.target_wdgs: [CalculatorTarget] = []
        for title, target_type in zip(titles, target_types):
            if title:
                title_wdg = QLabel(title)
                title_wdg.setTextFormat(Qt.TextFormat.RichText)
                title_wdg.setStyleSheet("font-weight: bold;"
                                        "" f"font-size: {fs}pt")
                title_wdgs.append(title_wdg)
            else:
                title_wdgs.append(None)
            target_wdg = CalculatorTarget()
            # text = target_type.to_display(format_='html')
            # target_wdg.setHtml(text)
            target_wdg.toolbar = self.toolbar
            target_wdg.navigation_bar = self.navigation_bar
            target_wdg.button_box = self.button_box

            self.target_wdgs.append(target_wdg)

        ##############
        # Set layout #
        ##############
        main_lyt = QVBoxLayout()
        main_lyt.addWidget(self.toolbar)
        # main_lyt.addWidget(QLabel(title))  # Remove?

        if self.task_title_widget:
            main_lyt.addWidget(self.task_title_widget)
        if self.task_widget:
            main_lyt.addWidget(self.task_widget)

        for title, target in zip(title_wdgs, self.target_wdgs):
            if title:
                main_lyt.addWidget(title)
            main_lyt.addWidget(target)

        main_lyt.addLayout(nav_lyt)
        self.setLayout(main_lyt)

        self.target_wdgs[0].setFocus()
        self.focused_target_idx = 0

        self.set_geometry()

    def update_size(self):
        self.resize(self.minimumSizeHint())
        self.setMinimumWidth(0)
        # print("Size updated!")

    def set_geometry(self, geometry=None):
        """
        Restore saved geometry if any, but adapt height to content.
        """
        settings = QSettings("deaduction")
        value = settings.value("calculator_targets/geometry")
        if value:
            self.restoreGeometry(value)
        elif geometry:
            self.setGeometry(geometry)
        else:
            return
        # Resize height window to minimum, but not width
        self.setMinimumWidth(self.width())
        QTimer.singleShot(1, self.update_size)

    def close(self):
        # Save window geometry
        settings = QSettings("deaduction")
        settings.setValue("calculator_targets/geometry", self.saveGeometry())
        self.window_closed.emit()

    def close_n_accept(self):
        self.close()
        self.accept()

    def reject(self):
        self.close()
        super().reject()

    @property
    def focused_target(self):
        idx = 0
        for target_wdg in self.target_wdgs:
            if target_wdg.hasFocus():
                self.focused_target_idx = idx
                break
            idx += 1

        return self.target_wdgs[self.focused_target_idx]

    def set_html(self, text):
        self.focused_target.setHtml(text)

    def set_focused_target_idx(self, idx):
        self.focused_target_idx = idx
        self.target_wdgs[idx].setFocus()
        # self.target_wdgs[idx].setEnabled(True)
        # for other_idx in range(len(self.target_wdgs)):
        #     if other_idx != idx:
        #         self.target_wdgs[other_idx].setEnabled(False)

    def on_focus_changed(self, old, new):
        """
        Systematically called when focus changes.
        If new focus is a target widget, then adjust focused_target_idx.
        If not, and focus is at some app widget,
        then steal focus for current target.
        """

        # print(f"Focus from {old} to {new}")
        idx = 0
        for wdg in self.target_wdgs:
            if wdg is new:
                self.set_focused_target_idx(idx)
                # Controller adjusts nav and history btns to new target:
                self.focus_has_changed.emit()
                # print(f"Target wdg n°{idx} has focus")
                return
            idx += 1

        # Focus has been stolen by some other guy!
        # (Isn't this a bit selfish?)
        #  --> Only if focus is on some specific widgets
        if new is not None:
            self.activateWindow()
            self.target_wdgs[self.focused_target_idx].setFocus()

            # print(f"Target wdg n°{self.focused_target_idx} steal focus")

        # for wdg_class in self.steal_focus_from_list:
        #     if isinstance(new, wdg_class):
        #         self.activateWindow()
        #         self.target_wdgs[self.focused_target_idx].setFocus()
        #
        #         print(f"Target wdg n°{self.focused_target_idx} steal focus")
