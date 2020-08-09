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
                                QInputDialog,
                                QMainWindow,
                                QMessageBox,
                                QToolBar,
                                QVBoxLayout,
                                QWidget)

from deaduction.dui.utils import        replace_delete_widget
from deaduction.dui.widgets import (    ActionButton,
                                        ActionButtonsWidget,
                                        LeanEditor,
                                        StatementsTreeWidget,
                                        StatementsTreeWidgetItem,
                                        ProofStatePOWidget,
                                        ProofStatePOWidgetItem,
                                        TargetWidget)
from deaduction.pylib.actions import (  Action,
                                        InputType,
                                        MissingParametersError,
                                        WrongUserInput)
import deaduction.pylib.actions.generic as generic
from deaduction.pylib.coursedata import (   Definition,
                                            Exercise,
                                            Theorem)
from deaduction.pylib.server.exceptions import FailedRequestError
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

        self.toggle_lean_editor_action = QAction(
                QIcon(str((icons_dir / 'lean_editor.png').resolve())),
                _('Toggle L∃∀N'), self)

        self.addAction(self.undo_action)
        self.addAction(self.redo_action)
        self.addAction(self.toggle_lean_editor_action)


class ExerciseCentralWidget(QWidget):
    """

    exercise and goal not stored as attributes
    """

    def __init__(self, exercise: Exercise):
        super().__init__()

        # ───────────── init layouts and boxes ───────────── #
        # I wish none of these were class atributes, but we need at
        # least self.__main_lyt and self.__context_lyt in the method
        # self.update_goal.

        self.__main_lyt     = QVBoxLayout()
        self.__context_lyt  = QVBoxLayout()
        context_actions_lyt = QHBoxLayout()
        actions_lyt         = QVBoxLayout()

        actions_gb = QGroupBox(_('Actions (transform context and target)'))
        context_gb = QGroupBox(_('Context (objects and properties)'))

        # ──────────────── init Actions area ─────────────── #
        self.logic_btns = ActionButtonsWidget(exercise.available_logic)
        self.proof_btns = ActionButtonsWidget(
                exercise.available_proof_techniques)

        statements           = exercise.available_statements
        outline              = exercise.course.outline
        self.statements_tree = StatementsTreeWidget(statements, outline)

        # ─────── init goal (Context area and target) ────── #
        self.objects_wgt = ProofStatePOWidget()
        self.props_wgt   = ProofStatePOWidget()
        self.target_wgt  = TargetWidget()

        # ───────────── put widgets in layouts ───────────── #
        # Actions
        actions_lyt.addWidget(self.logic_btns)
        actions_lyt.addWidget(self.proof_btns)
        actions_lyt.addWidget(self.statements_tree)
        actions_gb.setLayout(actions_lyt)

        # Context
        self.__context_lyt.addWidget(self.objects_wgt)
        self.__context_lyt.addWidget(self.props_wgt)
        context_gb.setLayout(self.__context_lyt)

        # https://i.kym-cdn.com/photos/images/original/001/561/446/27d.jpg
        context_actions_lyt.addWidget(context_gb)
        context_actions_lyt.addWidget(actions_gb)
        self.__main_lyt.addWidget(self.target_wgt)
        self.__main_lyt.addLayout(context_actions_lyt)

        self.setLayout(self.__main_lyt)

    @property
    def actions_buttons(self):

        return self.logic_btns.buttons + self.proof_btns.buttons 

    def freeze(self, yes=True):
        """
        Freeze interface.
        """

        to_freeze = [self.objects_wgt,
                     self.props_wgt,
                     self.logic_btns,
                     self.proof_btns,
                     self.statements_tree]
        for widget in to_freeze:
            widget.setEnabled(not yes)

    def update_goal(self, new_goal: Goal):
        """
        Update goal, that is target, objects and properties.
        """

        # Init context (objects and properties). Get them as two list of
        # (ProofStatePO, str), the str being the tag of the prop. or obj.
        # FIXME: tags
        new_context    = new_goal.tag_and_split_propositions_objects()
        new_target     = new_goal.target
        new_target_tag = '='  # new_target.future_tags[1]
        new_objects    = new_context[0]
        new_props      = new_context[1]

        new_objects_wgt = ProofStatePOWidget(new_objects)
        new_props_wgt   = ProofStatePOWidget(new_props)
        new_target_wgt  = TargetWidget(new_target, new_target_tag)

        # Replace in the layouts
        replace_delete_widget(self.__context_lyt,
                              self.objects_wgt, new_objects_wgt)
        replace_delete_widget(self.__context_lyt,
                              self.props_wgt, new_props_wgt)
        replace_delete_widget(self.__main_lyt,
                              self.target_wgt, new_target_wgt,
                              ~Qt.FindChildrenRecursively)

        # Set the attributes to the new values
        self.objects_wgt  = new_objects_wgt
        self.props_wgt    = new_props_wgt
        self.target_wgt   = new_target_wgt
        self.current_goal = new_goal


###############
# Main window #
###############


class ExerciseMainWindow(QMainWindow):

    window_closed         = Signal()
    __action_triggered    = Signal(ActionButton)
    __statement_triggered = Signal(StatementsTreeWidgetItem)

    def __init__(self, exercise: Exercise, servint: ServerInterface):
        super().__init__()

        # ─────────────────── Attributes ─────────────────── #

        self.exercise          = exercise
        self.current_goal      = None
        self.current_selection = []
        self.cw                = ExerciseCentralWidget(exercise)
        self.lean_editor       = LeanEditor()
        self.servint           = servint
        self.toolbar           = ExerciseToolbar()

        # ─────────────────────── UI ─────────────────────── #

        self.setCentralWidget(self.cw)
        self.addToolBar(self.toolbar)
        self.toolbar.redo_action.setEnabled(False)  # No history at beginning
        self.toolbar.undo_action.setEnabled(False)  # same

        # ──────────────── Signals and slots ─────────────── #

        # Actions area
        for action_button in self.cw.actions_buttons:
            action_button.action_triggered.connect(self.__action_triggered)
        self.cw.statements_tree.itemClicked.connect(self.__statement_triggered)

        # UI
        self.toolbar.toggle_lean_editor_action.triggered.connect(
                self.lean_editor.toggle)

        # Server communication
        self.servint.proof_state_change.connect(self.update_proof_state)
        self.servint.lean_file_changed.connect(self._update_lean_editor)
        self.servint.proof_no_goals.connect(self.fireworks)
        self.servint.nursery.start_soon(self.server_task)  # Start server task

    ###########
    # Methods #
    ###########

    def closeEvent(self, event):
        super().closeEvent(event)
        self.window_closed.emit()

    @property
    def current_selection_as_pspos(self):
        """
        Do not delete! Used many times.
        """

        return [item.proofstatepo for item in self.current_selection]

    def pretty_current_selection(self):
        msg = 'Current user selection: '
        msg += str([item.text() for item in self.current_selection])

        return msg

    def update_goal(self, new_goal: Goal):
        # Reset current context selection
        self.clear_current_selection()

        # Update UI and attributes
        self.cw.update_goal(new_goal)
        self.current_goal = new_goal

        # Reconnect Context area signals and slots
        self.cw.objects_wgt.itemClicked.connect(self.process_context_click)
        self.cw.props_wgt.itemClicked.connect(self.process_context_click)

    ##################################
    # Async tasks and server methods #
    ##################################
    
    # ─────────────────── Server task ────────────────── #
     
    async def server_task(self):
        self.freeze()
        await self.servint.exercise_set(self.exercise)
        self.freeze(False)

        async with qtrio.enter_emissions_channel(
                signals=[self.lean_editor.editor_send_lean,
                         self.toolbar.redo_action.triggered,
                         self.window_closed,
                         self.toolbar.undo_action.triggered,
                         self.__action_triggered,
                         self.__statement_triggered]) as emissions:
            async for emission in emissions.channel:
                if emission.is_from(self.lean_editor.editor_send_lean):
                    await self.process_async_signal(self._server_send_editor_lean)

                elif emission.is_from(self.toolbar.redo_action.triggered):
                    # No need to call self.update_goal, this emits the
                    # signal proof_state_change of which
                    # self.update_goal is a slot
                    await self.process_async_signal(self.servint.history_redo)

                elif emission.is_from(self.toolbar.undo_action.triggered):
                    await self.process_async_signal(self.servint.history_undo)

                elif emission.is_from(self.window_closed):
                    break

                elif emission.is_from(self.__action_triggered):
                    # TODO: comment, what is emission.args[0]?
                    await self.process_async_signal(partial(self._server_call_action,
                                                            emission.args[0]))

                elif emission.is_from(self.__statement_triggered):
                    await self.process_async_signal(partial(self._server_call_statement,
                                                            emission.args[0]))

    # ──────────────── Template function ─────────────── #
    
    async def process_async_signal(self, process_function: Callable):
        self.freeze(True)

        try:
            await process_function()
        except FailedRequestError as e:
            # Display an error message
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle(_('Action not understood'))
            msg_box.setText(_('Action not understood'))

            detailed = ""
            for error in e.errors:
                rel_line_number = error.pos_line \
                        - self.exercise.lean_begin_line_number
                detailed += f'* at {rel_line_number}: {error.text}\n'

            msg_box.setDetailedText(detailed)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()

            # Abort and go back to last goal
            await self.servint.history_undo()

        finally:
            self.freeze(False)
            # Required for the history is always changed with signals
            self.toolbar.undo_action.setEnabled(
                    not self.servint.lean_file.history_at_beginning)
            self.toolbar.redo_action.setEnabled(
                    not self.servint.lean_file.history_at_end)

    # ─────────────── Specific functions ─────────────── #
    # To be called as process_function in the above

    async def _server_call_action(self, action_btn: ActionButton):
        action = action_btn.action
        user_input = []

        # Send action and catch exception when user needs to:
        #   - choose A or B when having to prove (A OR B) ;
        #   - enter an element when clicking on 'exists' button.
        while True:
            try:
                if user_input == []:
                    code = action.run(self.current_goal,
                                      self.current_selection_as_pspos)
                else:
                    code = action_btn.action.run(self.current_goal,
                            self.current_selection, user_input)
            except MissingParametersError as e:
                if e.input_type == InputType.Text:
                    text, ok = QInputDialog.getText(action_btn,
                            e.title, e.output)
                elif e.input_type == InputType.Choice:
                    text, ok = QInputDialog.getItem(action_btn,
                            _("Choose element"), "", e.list_of_choices,
                            0, False)
                if ok:
                    user_input.append(text)
                else:
                    break
            except WrongUserInput:
                self.clear_current_selection()
                break
            else:
                await self.servint.code_insert(action.caption, code)
                break

    async def _server_call_statement(self, item: StatementsTreeWidgetItem):
        # Do nothing is user clicks on a node
        if isinstance(item, StatementsTreeWidgetItem):
            item.setSelected(False)
            statement = item.statement

            if isinstance(statement, Definition):
                code = generic.action_definition(self.current_goal,
                        self.current_selection_as_pspos, statement)
            elif isinstance(statement, Theorem):
                code = generic.action_theorem(self.current_goal,
                        self.current_selection_as_pspos, statement)

            await self.servint.code_insert(statement.pretty_name, code)

    async def _server_send_editor_lean(self):
        await self.servint.code_set(_('Code from editor'),
                self.lean_editor.code_get())

    #########
    # Slots #
    #########

    @Slot()
    def clear_current_selection(self):
        log.debug('Clearing user selection')
        for item in self.current_selection:
            item.mark_user_selected(False)

        self.current_selection = []
        log.debug(self.pretty_current_selection())

    @Slot()
    def freeze(self, yes=True):
        self.cw.freeze(yes)
        self.toolbar.setEnabled(not yes)

    @Slot()
    def fireworks(self):
        QMessageBox.information(self, _('Target solved'), _('Target solved!'),
                                QMessageBox.Ok)

    @Slot(ProofStatePOWidgetItem)
    def process_context_click(self, item: ProofStatePOWidgetItem):
        log.debug('Recording user selection')
        item.setSelected(False)

        if item not in self.current_selection:
            item.mark_user_selected(True)
            self.current_selection.append(item)
        else:
            item.mark_user_selected(False)
            self.current_selection.remove(item)

        log.debug(self.pretty_current_selection())

    @Slot()
    def _update_lean_editor(self):
        self.lean_editor.code_set(self.servint.lean_file.inner_contents)

    @Slot(ProofState)
    def update_proof_state(self, proofstate: ProofState):
        self.update_goal(proofstate.goals[0])
