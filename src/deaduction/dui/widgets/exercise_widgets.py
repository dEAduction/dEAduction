"""
########################################################
# exercisewidget.py : provide the ExerciseWidget class #
########################################################

Author(s)      : - Kryzar <antoine@hugounet.com>
                 - Florian Dupeyron <florian.dupeyron@mugcat.fr>
Maintainers(s) : - Kryzar <antoine@hugounet.com>
                 - Florian Dupeyron <florian.dupeyron@mugcat.fr>
Date           : July 2020

Copyright (c) 2020 the dEAduction team

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

from functools import           partial
import logging
from gettext import gettext as  _
from pathlib import Path
import trio
from typing import              Callable
import qtrio

from PySide2.QtCore import (    Signal,
                                Slot,
                                Qt)
from PySide2.QtGui import       QIcon
from PySide2.QtWidgets import ( QAction,
                                QDesktopWidget,
                                QGroupBox,
                                QHBoxLayout,
                                QMainWindow,
                                QToolBar,
                                QVBoxLayout,
                                QWidget)

from deaduction.dui.utils import        replace_delete_widget
from deaduction.dui.widgets import (    ActionButton,
                                        ActionButtonsWidget,
                                        LeanEditor,
                                        StatementsTreeWidget,
                                        ProofStatePOWidget,
                                        ProofStatePOWidgetItem,
                                        TargetWidget)
from deaduction.pylib.actions import    Action
from deaduction.pylib.coursedata import Exercise
from deaduction.pylib.mathobj import (  Goal,
                                        ProofState)
from deaduction.pylib.server import     ServerInterface

log = logging.getLogger(__name__)


###########
# Widgets #
###########


class ExerciseToolbar(QToolBar):

    def __init__(self):
        super().__init__(_('Toolbar'))

        icons_dir = Path('share/graphical_resources/icons/')
        self.undo_action = QAction(
                QIcon(str((icons_dir / 'undo_action.png').resolve())),
                _('Undo action'), self)
        self.redo_action = QAction(
                QIcon(str((icons_dir / 'redo_action.png').resolve())),
                _('Redo action'), self)
        self.clear_selection_action = QAction(
                QIcon(str((icons_dir / 'clear_selection.png').resolve())),
               _('Clear selection'), self)

        self.toggle_lean_editor_action = QAction(
                QIcon(str((icons_dir / 'lean_editor.png').resolve())),
                _('Toggle L∃∀N'), self)

        self.addAction(self.undo_action)
        self.addAction(self.redo_action)
        self.addAction(self.clear_selection_action)
        self.addAction(self.toggle_lean_editor_action)


class ExerciseCentralWidget(QWidget):

    ################
    # Init methods #
    ################
    
    def _init_all_layout_boxes(self):
        # TODO: draw the damn thing

        # Layouts
        self._main_lyt = QVBoxLayout()
        self._context_actions_lyt = QHBoxLayout()
        self._context_lyt = QVBoxLayout()
        self._actions_lyt = QVBoxLayout()

        # Group boxes
        self._actions_gb = QGroupBox(_('Actions (transform context)'))
        self._context_gb = QGroupBox(_('Context (properties and objects)'))

    def _init_actions(self):
        # Init tool buttons
        self.logic_btns = ActionButtonsWidget(self.exercise.available_logic)
        # Init proof techniques buttons
        self.proof_btns = ActionButtonsWidget(
                self.exercise.available_proof_techniques)
        # Init statements tree
        statements = self.exercise.available_statements
        outline = self.exercise.course.outline
        self.statements_tree = StatementsTreeWidget(statements, outline)

    def _init_goal(self):
        # Create empty widgets while waiting for Lean
        self.objects_wgt = ProofStatePOWidget()
        self.props_wgt = ProofStatePOWidget()
        self.target_wgt = TargetWidget()

    def _init_put_widgets_in_layouts(self):
        # Actions
        self._actions_lyt.addWidget(self.logic_btns)
        self._actions_lyt.addWidget(self.proof_btns)
        self._actions_lyt.addWidget(self.statements_tree)
        self._actions_gb.setLayout(self._actions_lyt)

        # Context
        self._context_lyt.addWidget(self.objects_wgt)
        self._context_lyt.addWidget(self.props_wgt)
        self._context_gb.setLayout(self._context_lyt)

        # https://i.kym-cdn.com/photos/images/original/001/561/446/27d.jpg
        self._context_actions_lyt.addWidget(self._context_gb)
        self._context_actions_lyt.addWidget(self._actions_gb)
        self._main_lyt.addWidget(self.target_wgt)
        self._main_lyt.addLayout(self._context_actions_lyt)

    def __init__(self, exercise: Exercise):
        super().__init__()
        self.exercise = exercise
        self._init_all_layout_boxes()
        self._init_actions()
        self._init_goal()
        self._init_put_widgets_in_layouts()
        self.setLayout(self._main_lyt)


###############
# Main window #
###############


class ExerciseMainWindow(QMainWindow):

    window_closed = Signal()
    __action_triggered = Signal(ActionButton)

    ################
    # Init methods #
    ################

    def __init__(self, exercise: Exercise, servint: ServerInterface):
        super().__init__()
        self.exercise = exercise
        self.current_goal = None
        self.cw = ExerciseCentralWidget(self.exercise)
        self.current_context_selection = []
        self.lean_editor = LeanEditor()
        self.servint = servint
        self.toolbar = ExerciseToolbar()

        self.setCentralWidget(self.cw)
        self.addToolBar(self.toolbar)

        # There is no history at the beginning
        self.toolbar.redo_action.setEnabled(False)
        self.toolbar.undo_action.setEnabled(False)

        # Signals and slots
        self.connect_actions_signals_slots()
        self.servint.proof_state_change.connect(self.update_proof_state)
        self.servint.lean_file_changed.connect(self._update_lean_editor)

        # Start server task
        self.servint.nursery.start_soon(self.server_task)

    #################
    # Other methods #
    #################

    def connect_actions_signals_slots(self):
        # Actions buttons
        for logic_btn in self.cw.logic_btns.buttons:
            logic_btn.action_triggered.connect(self.__action_triggered)

        # Proof buttons
        for proof_btn in self.cw.proof_btns.buttons:
            proof_btn.action_triggered.connect(self.__action_triggered)

        # Toolbar
        self.toolbar.clear_selection_action.triggered.connect(
                self.clear_user_selection)
        self.toolbar.toggle_lean_editor_action.triggered.connect(
                self.lean_editor.toggle)

    def connect_context_signals_slots(self):
        # Objects and properties lists
        self.cw.objects_wgt.itemClicked.connect(
                self.process_context_click)
        self.cw.props_wgt.itemClicked.connect(
                self.process_context_click)

        # Proofstate (=> goal) change
        self.servint.proof_state_change.connect(self.update_proof_state)

    def closeEvent(self, event):
        super().closeEvent(event)
        self.window_closed.emit()

    @property
    def current_context_selection_as_pspos(self):
        return [item.proofstatepo for item in self.current_context_selection]

    def pretty_user_selection(self):
        msg = 'Current user selection: '
        msg += str([item.text() for item in self.current_context_selection])

        return msg

    def update_goal(self, new_goal: Goal):

        # Init context (objects and properties). Get them as two list of
        # (ProofStatePO, str), the str being the tag of the prop. or obj.
        new_context = new_goal.tag_and_split_propositions_objects()
        new_objects_wgt = ProofStatePOWidget(new_context[0])
        new_props_wgt = ProofStatePOWidget(new_context[1])
        new_target = new_goal.target
        # TODO: set real tag value
        new_target_tag = '=' # new_target.future_tags[1]
        new_target_wgt = TargetWidget(new_target, new_target_tag)

        # Replace in the layouts
        replace_delete_widget(self.cw._context_lyt,
                              self.cw.objects_wgt, new_objects_wgt)
        replace_delete_widget(self.cw._context_lyt,
                              self.cw.props_wgt, new_props_wgt)
        replace_delete_widget(self.cw._main_lyt,
                              self.cw.target_wgt, new_target_wgt,
                              ~Qt.FindChildrenRecursively)

        # Set the attributes to the new values
        self.cw.objects_wgt = new_objects_wgt
        self.cw.props_wgt = new_props_wgt
        self.cw.target_wgt = new_target_wgt
        self.current_goal = new_goal

        # Reconnect signals and slots
        self.connect_context_signals_slots()

    ###############
    # Async tasks #
    ###############
   
    async def server_task(self):
        self.freeze()
        await self.servint.exercise_set(self.exercise)
        self.freeze(False)
        async with qtrio.enter_emissions_channel(
            signals=[self.window_closed,
                     self.__action_triggered,
                     self.toolbar.undo_action.triggered,
                     self.toolbar.redo_action.triggered,
                     self.lean_editor.editor_send_lean]
        ) as emissions:
            async for emission in emissions.channel:
                if emission.is_from(self.window_closed):
                    break
                elif emission.is_from(self.__action_triggered):
                    await self.process_async_signal(
                            partial(self._server_call_action,
                                    emission.args[0])
                    )
                elif emission.is_from(self.toolbar.undo_action.triggered):
                    # No need to call self.update_goal, this block
                    # emits the signal proof_state_change of which
                    # self.update_goal is a slot, see 
                    # self.connect_context_signals_slots.
                    await self.process_async_signal(self.servint.history_undo)
                elif emission.is_from(self.toolbar.redo_action.triggered):
                    await self.process_async_signal(self.servint.history_redo)
                elif emission.is_from(self.lean_editor.editor_send_lean):
                    await self.process_async_signal(
                            self._server_send_editor_lean)

    ##################
    # Server methods #
    ##################

    async def process_async_signal(self, process_function: Callable):
        self.freeze(True)
        try:
            await process_function()
        finally:
            self.freeze(False)
            # Required for the history is always changed with signals
            self.toolbar.undo_action.setEnabled(not
                    self.servint.lean_file.history_at_beginning)
            self.toolbar.redo_action.setEnabled(not
                    self.servint.lean_file.history_at_end)

    async def _server_call_action(self, action_btn: ActionButton):
        action = action_btn.action
        code = action.run(self.current_goal,
                          self.current_context_selection_as_pspos)
        await self.servint.code_insert(action.caption, code)

    async def _server_send_editor_lean(self):
        await self.servint.code_set(_('Code from editor'),
                self.lean_editor.code_get())

    #########
    # Slots #
    #########

    @Slot()
    def clear_user_selection(self):
        log.debug('Clearing user selection')
        for item in self.current_context_selection:
            item.mark_user_selected(False)

        self.current_context_selection = []
        log.debug(self.pretty_user_selection())

    @Slot()
    def freeze(self, yes=True):
        to_freeze = [self.toolbar,
                     self.cw.objects_wgt,
                     self.cw.props_wgt,
                     self.cw.logic_btns,
                     self.cw.proof_btns,
                     self.cw.statements_tree]

        for widget in to_freeze:
            widget.setEnabled(not yes)

    @Slot(ProofStatePOWidgetItem)
    def process_context_click(self, item: ProofStatePOWidgetItem):
        log.debug('Recording user selection')
        item.setSelected(False)

        if item not in self.current_context_selection:
            item.mark_user_selected(True)
            self.current_context_selection.append(item)
        else:
            item.mark_user_selected(False)
            self.current_context_selection.remove(item)

        log.debug(self.pretty_user_selection())

    @Slot()
    def _update_lean_editor(self):
        self.lean_editor.code_set(self.servint.lean_file.inner_contents)

    @Slot(ProofState)
    def update_proof_state(self, proofstate: ProofState):
        self.update_goal(proofstate.goals[0])
