"""
##############################################################
# exercise_main_window.py : Provide ExerciseMainWindow class #
##############################################################

Author(s)      : Kryzar <antoine@hugounet.com>
Maintainers(s) : Kryzar <antoine@hugounet.com>
Date           : March 2021

Copyright (c) 2021 the dEAduction team

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

from functools import partial
import                logging
from typing import    Callable
import                qtrio
from copy import      copy, deepcopy

from PySide2.QtCore import (    Signal,
                                Slot,
                                QEvent )
from PySide2.QtWidgets import ( QInputDialog,
                                QMainWindow,
                                QMessageBox )

from deaduction.dui.elements            import ( ActionButton,
                                                 LeanEditor,
                                                 StatementsTreeWidgetItem,
                                                 MathObjectWidget,
                                                 MathObjectWidgetItem )
from deaduction.dui.primitives          import   ButtonsDialog
from deaduction.pylib.config.i18n       import   _
from deaduction.pylib.memory            import ( Journal,
                                                 EventNature)
from deaduction.pylib.actions           import ( InputType,
                                                 CodeForLean,
                                                 MissingParametersError,
                                                 WrongUserInput)
import deaduction.pylib.actions.generic as       generic
from deaduction.pylib.coursedata        import ( Definition,
                                                 Exercise,
                                                 Theorem)
from deaduction.pylib.mathobj           import ( MathObject,
                                                 Goal,
                                                 ProofState,
                                                 ProofStep,
                                                 Proof )
from deaduction.pylib.server.exceptions import   FailedRequestError
from deaduction.pylib.server            import   ServerInterface

from ._exercise_main_window_widgets     import ( ExerciseCentralWidget,
                                                 ExerciseStatusBar,
                                                 ExerciseToolBar )
import deaduction.pylib.config.vars      as      cvars

log = logging.getLogger(__name__)


class ExerciseMainWindow(QMainWindow):
    # TODO: explain better communication and who talks to who?
    """
    This class is responsible for both:
        - managing the whole interface for exercises;
        - communicating with a so-called server interface (self.servint, not
          instantiated in this class): a middle man between the interface and
          L∃∀N.

    User interface, server interface and L∃∀N server are different entities
    which remain separated by design; Qt signals and slots are used for
    communication between them. For the interface, self instantiates
    ExerciseCentralWidget, a toolbar, and probably more things in the future.
    For the communication with self.servint, self:
        1. stores user selection of math. objects or properties
           (self.current_selection);
        2. detects when an action button (in self.ecw.logic_btns or
           in self.ecw.proof_btns) or a statement (in
           self.ecw.statements_tree) is clicked on;
        3. sends (the current goal, current selection) and ((clicked
           action button (with self.__server_call_action)) xor (clicked
           statement (with self.__server_call_statement))) to the server
           interface;
        4. waits for some response (e.g. a new goal, an exception asking
           for new user parameters).
    As said, this class both sends and receives data to / from a server
    interface.
        - Sending data to the server inteface (self.servint) is achieved
          in the method server_task with signals and slots. More
          precisely, this methods receives signals (async with
          qtrio.enter_emissions_channel(signals …)) and calls functions
          / methods accordingly. Beware that this is not exactly Qt's
          native signals / slots mechanism.
        - Receiving data from the server interface achieved with signals
          and slots. Such signals are simply connected to Qt Slots in
          self.__init__; this is much simpler than sending data.

    Finally, all of this uses asynchronous processes (keywords async and
    await) using trio and qtrio.

    :attribute exercise Exercise: The instance of the Exercise class
        representing the exercise to be solved by the user, instantiated
        in deaduction.dui.__main__.py.
    :attribute current_goal Goal: The current goal, which contains the
        tagged target, tagged math. objects and tagged math. properties.
    :attribute current_selection [MathObjectWidgetItem]: The ordered of
        currently selected math. objects and properties by the user.
    :attribute ecw ExerciseCentralWidget: The instance of
        ExerciseCentralWidget instantiated in self.__init__, see
        ExerciseCentraiWidget.__doc__.
    :attribute lean_editor LeanEditor: A text editor to live-edit lean
        code.
    :attribute servint ServerInterface: The instance of ServerInterface
        for the session, instantiated in deaduction.dui.__main__.py.
    :attribute toolbar QToolBar: The toolbar.
    :attribute journal Journal: used to store the list of all events
        occurring in the interface, both practical and logical.
    :attribute exercise_solved bool: initialised to False, becomes True the
        first time target is solved.
    :attribute test_mode bool: True when auto testing.
    :attribute proof_step ProofStep: this class store all the data of the
        current proof step : user selection, button or statement triggered,
        user_input, CodeForLean, success or error msgs, and proof_state. It
        also stores memories of the proof, in particular the goal counters.
    :attribute displayed_proof_step ProofStep: This contains data of the
        ProofStep that was previously displayed by the ui. This ProofStep is
        not necessarily the previous proof step in the logical order,
        in case of undoing: the logically previous step is stored in the
        lean_file and may be retrieved using the logically_previous_proof_step
         property.
    """

    window_closed                   = Signal()
    change_exercise                 = Signal()
    __action_triggered              = Signal(ActionButton)
    __apply_math_object_triggered   = Signal(MathObjectWidget)
    __statement_triggered           = Signal(StatementsTreeWidgetItem)
    proof_step_updated              = Signal()
    ui_updated                      = Signal()

    def __init__(self, exercise: Exercise, servint: ServerInterface):
        """
        Init self with an instance of the exercise class and an instance of the
        class ServerInterface. Both those instances are created in
        deaduction.dui.__main__.py. See self.__doc__.

        :param exercise: The instance of the Exercise class representing
            the exercise to be solved by the user.
        :param servint: The instance of the ServerInterface class in charge of
            communicating with vim.
        """

        super().__init__()
        self.setWindowTitle(f'{exercise.pretty_name} — d∃∀duction')

        # ─────────────────── Attributes ─────────────────── #

        self.target_selected_by_default = cvars.get(
                            'functionality.target_selected_by_default', False)
        self.exercise             = exercise
        self.current_goal         = None
        self.current_selection    = []
        self._target_selected     = False
        self.ecw                  = ExerciseCentralWidget(exercise)
        self.lean_editor          = LeanEditor()
        self.servint              = servint
        self.toolbar              = ExerciseToolBar()
        self.journal              = Journal()
        self.proof_step           = ProofStep()
        self.displayed_proof_step = None
        self.exercise_solved      = False
        self.test_mode            = False

        # ─────────────────────── UI ─────────────────────── #

        self.setCentralWidget(self.ecw)
        self.addToolBar(self.toolbar)
        self.toolbar.redo_action.setEnabled(False)  # No history at beginning
        self.toolbar.undo_action.setEnabled(False)  # same
        self.toolbar.rewind.setEnabled(False)  # same

        # Status Bar
        self.statusBar = ExerciseStatusBar(self)
        self.setStatusBar(self.statusBar)

        # ──────────────── Signals and slots ─────────────── #

        # Actions area
        for action_button in self.ecw.actions_buttons:
            action_button.action_triggered.connect(self.__action_triggered)
        self.ecw.statements_tree.itemClicked.connect(self.__statement_triggered)

        # UI
        self.toolbar.toggle_lean_editor_action.triggered.connect(
                self.lean_editor.toggle)

        # Server communication
        self.servint.proof_state_change.connect(self.update_proof_state)
        self.servint.lean_file_changed.connect(self.__update_lean_editor)
        self.servint.proof_no_goals.connect(self.fireworks)
        self.servint.effective_code_received.connect(
                                                self.servint.history_replace)
        self.servint.effective_code_received.connect(self.store_effective_code)
        self.toolbar.change_exercise_action.triggered.connect(
                                                    self.change_exercise)
        self.servint.nursery.start_soon(self.server_task)  # Start server task

    ###########
    # Methods #
    ###########

    @property
    def lean_file(self):
        """ Virtual file containing the Lean code and its history."""
        return self.servint.lean_file

    @property
    def logically_previous_proof_step(self):
        """
        The previous proof step in the logical order is always stored in the
        previous entry of lean_file's history. This is NOT the proof step
        that was previously displayed by the ui in case of history undo or
        rewind (which is stored in self.displayed_proof_step).
        """
        return self.lean_file.previous_proof_step

    @property
    def objects(self):
        """ MathObject's instances displayed as objects"""
        return [item.mathobject for item in self.ecw.objects_wgt.items]

    @property
    def properties(self):
        """ MathObject's instances displayed as properties"""
        return [item.mathobject for item in self.ecw.props_wgt.items]

    @property
    def target_selected(self):
        """
        Boolean, True iff target is selected.
        """
        if not self.target_selected_by_default:
            return self._target_selected
        else:
            # Target is selected by default if current_selection is empty
            return not self.current_selection

    @target_selected.setter
    def target_selected(self, target_selected):
        self._target_selected = target_selected

    def closeEvent(self, event: QEvent):
        """
        Overload native Qt closeEvent method — which is called when self
        is closed — to send the signal self.window_closed.

        :param event: Some Qt mandatory thing.
        """

        super().closeEvent(event)
        self.lean_editor.close()
        self.window_closed.emit()

    @property
    def current_selection_as_mathobjects(self):
        """
        Do not delete, used many times! Return the current selection as
        an ordered list of instances of the class MathObject directly.

        :return: See above.
        """

        return [item.mathobject for item in self.current_selection]

    def pretty_current_selection(self) -> str:
        """
        Return the current selection as a string, for display.

        :return: See above.
        """

        msg = 'Current user selection: '
        msg += str([item.text() for item in self.current_selection])

        return msg

    async def simulate(self, proof_step: ProofStep):
        """
        This method simulate proof_step by selecting the selection and
        checking button or statement stored in proof_step. This is called
        when redoing. Note that the corresponding actions are NOT called,
        since this would modify history of the lean_file.
        The method is asynchroneous
        """

        # Light target on/off as needed
        if proof_step.selection:
            self.ecw.target_wgt.mark_user_selected(False)
        else:
            self.ecw.target_wgt.mark_user_selected(True)
        # Light on selection
        for item in self.ecw.props_wgt.items + self.ecw.objects_wgt.items:
            for math_object in proof_step.selection:
                if item.mathobject == math_object:
                    item.mark_user_selected(True)
        # Check button or statement
        if isinstance(proof_step.button, ActionButton):
            await proof_step.button.simulate(duration=0.3)
        elif isinstance(proof_step.statement_item, StatementsTreeWidgetItem):
            await proof_step.statement_item.simulate(duration=0.3)
        # Light off selection synchronously
        for item in self.ecw.props_wgt.items:
            item.mark_user_selected(False)

    def update_goal(self, new_goal: Goal):
        """
        Change widgets (target, math. objects and properties) to
        new_goal and update internal mechanics accordingly.

        :param new_goal: The new goal to update / set the interface to.
        """
        if new_goal is self.current_goal:  # No update needed
            self.ui_updated.emit()
            return

        # Get previous goal and set tags
        if self.logically_previous_proof_step:
            # Fixme: not when undoing history ?
            previous_goal = self.logically_previous_proof_step.goal
            Goal.compare(new_goal, previous_goal)  # Set tags

        # Goal count to be displayed next to the target
        goal_count = f'  {self.proof_step.current_goal_number} / ' \
                     f'{self.proof_step.total_goals_counter}'

        # Reset current context selection
        # Here we do not use empty_current_selection since Widgets may have
        # been deleted, and anyway this is cosmetics since  widgets are
        # destroyed and re-created by "self.ecw.update_goal" just below
        self.current_selection = []

        # Update UI and attributes. Target stay selected if it was.
        self.ecw.update_goal(new_goal, goal_count)
        self.ecw.target_wgt.mark_user_selected(self.target_selected)
        self.current_goal = new_goal

        # Reconnect Context area signals and slots
        self.ecw.objects_wgt.itemClicked.connect(self.process_context_click)
        self.ecw.props_wgt.itemClicked.connect(self.process_context_click)

        self.ecw.target_wgt.mouseReleaseEvent = self.process_target_click
        if hasattr(self.ecw, "action_apply_button"):
            self.ecw.objects_wgt.apply_math_object_triggered.connect(
                self.__apply_math_object_triggered)
            self.ecw.props_wgt.apply_math_object_triggered.connect(
                self.__apply_math_object_triggered)

        self.ui_updated.emit()  # This signal is used for autotest.

    ##################################
    # Async tasks and server methods #
    ##################################

    # Most important methods for communication with the server interface
    # (self.servint) are defined here:
    #   - server_task is the director which listens to signals and calls
    #     other methods;
    #   - process_async_signal is a wrapper method which allows
    #     specific methods to be properly called in server_task by
    #     putting them in try… except… blocks, etc;
    #   - other methods are specific methods with a specific task,
    #     called when a particular signal is received in server_task.

    # ─────────────────── Server task ────────────────── #

    async def server_task(self):
        """
        This method handles sending user data and actions to the server
        interface (self.servint). It listens to signals and calls
        specific methods for those signals accordingly. Async / await
        processes are used in accordance to what is done in the server
        interface. This method is called in self.__init__.
        The user actions are stored in self.proof_step.
        """

        self.freeze()
        await self.servint.exercise_set(self.exercise)
        self.freeze(False)

        async with qtrio.enter_emissions_channel(
                signals=[self.lean_editor.editor_send_lean,
                         self.toolbar.redo_action.triggered,
                         self.toolbar.undo_action.triggered,
                         self.toolbar.rewind.triggered,
                         self.__action_triggered,
                         self.__statement_triggered,
                         self.__apply_math_object_triggered]) as emissions:
            async for emission in emissions.channel:
                self.statusBar.erase()

                if emission.is_from(self.lean_editor.editor_send_lean):
                    await self.process_async_signal(self.__server_send_editor_lean)

                elif emission.is_from(self.toolbar.redo_action.triggered)\
                        and not self.lean_file.history_at_end:
                    # No need to call self.update_goal, this emits the
                    # signal proof_state_change of which
                    # self.update_goal is a slot.
                    # The UI simulate the redone step if possible.
                    self.proof_step.button = 'history_redo'
                    proof_step = self.lean_file.next_proof_step
                    if proof_step:
                        await self.simulate(proof_step)
                    await self.process_async_signal(self.servint.history_redo)

                elif emission.is_from(self.toolbar.undo_action.triggered):
                    self.proof_step.button = 'history_undo'
                    await self.process_async_signal(self.servint.history_undo)

                elif emission.is_from(self.toolbar.rewind.triggered):
                    self.proof_step.button = 'history_rewind'
                    await self.process_async_signal(self.servint.history_rewind)

                elif emission.is_from(self.window_closed):
                    break

                elif emission.is_from(self.__action_triggered):
                    # emission.args[0] is the ActionButton triggered by user
                    self.proof_step.button = emission.args[0]
                    await self.process_async_signal(partial(
                            self.__server_call_action, emission.args[0]))

                elif emission.is_from(self.__statement_triggered):
                    # emission.args[0] is the StatementTreeWidgetItem
                    # triggered by user
                    if hasattr(emission.args[0], 'statement'):
                        self.proof_step.statement_item = emission.args[0]
                    await self.process_async_signal(partial(
                            self.__server_call_statement, emission.args[0]))

                elif emission.is_from(self.__apply_math_object_triggered):
                    self.proof_step.button = self.ecw.action_apply_button
                    await self.__server_call_apply(emission.args[0])

    # ──────────────── Template function ─────────────── #

    async def process_async_signal(self, process_function: Callable):
        """
        This methods wraps specific methods to be called when a specific
        signal is received in server_task. First, try to call
        process_function and waits for a response. An exception may be
        risen to ask user for additional info (e.g. a math object).
        Note that the current goal is modified from elsewhere in the
        program (signal self.servint.proof_state_change.connect), not
        here! This is done before the finally bloc. And finally, update
        the last interface elements to be updated.
        """

        self.freeze(True)

        try:
            await process_function()
        except FailedRequestError as error:
            self.proof_step.error_type = 2
            self.proof_step.error_msg = error.message

            # Abort and go back to last goal
            await self.servint.history_delete()

        finally:
            if not self.lean_file.current_proof_step.no_more_goal:
                self.freeze(False)
            else:  # If no more goals, disable actions but enable toolbar
                self.ecw.freeze(True)
                self.toolbar.setEnabled(True)
            # Required because history is always changed with signals
            self.toolbar.undo_action.setEnabled(
                    not self.servint.lean_file.history_at_beginning)
            self.toolbar.rewind.setEnabled(
                    not self.servint.lean_file.history_at_beginning)
            self.toolbar.redo_action.setEnabled(
                    not self.servint.lean_file.history_at_end)

    # ─────────────── Specific functions ─────────────── #
    # To be called as process_function in the above

    async def __server_call_action(self,
                                   action_btn: ActionButton,
                                   auto_selection=None,
                                   auto_user_input=None):
        """
        Call the action corresponding to the action_btn

        The action is linked to the action_btn in the "action" field. Then, we
        can try to call the action in a loop. As we doesn't now if the action
        needs some parameters or not, it may throw the
        "MissingParametersErrorException". This exception indicates that we
        need to ask some info to the user. So, we ask what the user wants, then
        we redo one loop iteration, feeding the action with the new input.

        Another exception that can occur is the WrongUserInput exception. At
        this point, the user entered some wrong data, we display an error
        in the status bar and stop.

        Note the usage of the try .. else statement.

        :param action_btn: the button corresponding to the action we want to
        call
        """

        action     = action_btn.action
        log.debug(f'Calling action {action.symbol}')
        # Send action and catch exception when user needs to:
        #   - choose A or B when having to prove (A OR B) ;
        #   - enter an element when clicking on 'exists' button.
        #   - and so on.
        if auto_selection:  # For autotest
            selection = auto_selection
            self.proof_step.selection = selection
        else:
            selection = self.current_selection_as_mathobjects
            self.proof_step.selection = selection

        if auto_user_input:
            user_input = auto_user_input
        else:
            user_input = []

        while True:
            try:
                if not user_input:
                    lean_code = action.run(
                        self.proof_step,
                        selection,  # (TODO: selection is stored in proof_step)
                        target_selected=self.target_selected)
                else:
                    lean_code = action.run(
                        self.proof_step,
                        selection,
                        user_input,
                        target_selected=self.target_selected)
            except MissingParametersError as e:
                if e.input_type == InputType.Text:
                    choice, ok = QInputDialog.getText(action_btn,
                                                      e.title,
                                                      e.output)
                elif e.input_type == InputType.Choice:
                    choice, ok = ButtonsDialog.get_item(e.choices,
                                                        e.title,
                                                        e.output)
                if ok:
                    user_input.append(choice)
                else:
                    break
            except WrongUserInput as error:
                self.proof_step.user_input = user_input
                self.proof_step.error_type = 1
                self.proof_step.error_msg = error.message

                self.empty_current_selection()
                self.update_proof_state(self.displayed_proof_step.proof_state)
                break
            else:
                self.proof_step.lean_code = lean_code
                self.proof_step.user_input = user_input
                # Update lean_file and call Lean server
                await self.servint.code_insert(action.symbol, lean_code)
                break

    async def __server_call_apply(self, item: MathObjectWidgetItem):
        """
        This function is called when user double-click on an item in the
        context area The item is added to the end of the current_selection, and
        the action corresponding to the "apply" button is called.
        """

        item.mark_user_selected(True)
        # Put double-clicked item on last position in current_selection
        # NB: DO NOT add item to selection since the  process_context_click
        # will already do this
        if item in self.current_selection:
            self.current_selection.remove(item)
        # Emulate click on 'apply' button
        self.ecw.action_apply_button.animateClick(msec=500)

    async def __server_call_statement(self,
                                      item: StatementsTreeWidgetItem,
                                      auto_selection=None):
        """
        This function is called when the user clicks on a Statement he wants to
        apply. The statement can be either a Definition or a Theorem. the code
        is then inserted to the server.
        """
        if auto_selection:
            selection = auto_selection
            self.proof_step.selection = selection
        else:
            selection = self.current_selection_as_mathobjects
            self.proof_step.selection = selection

        # Do nothing if user clicks on a node
        if isinstance(item, StatementsTreeWidgetItem):
            try:
                item.setSelected(False)
                statement = item.statement

                if isinstance(statement, Definition):
                    lean_code = generic.action_definition(
                        self.proof_step,
                        selection,
                        statement,
                        self.target_selected)
                elif isinstance(statement, Theorem):
                    lean_code = generic.action_theorem(
                        self.proof_step,
                        selection,
                        statement,
                        self.target_selected)

            except WrongUserInput as error:
                self.empty_current_selection()
                self.proof_step.error_type = 1
                self.proof_step.error_msg = error.message
                self.update_proof_state(self.displayed_proof_step.proof_state)

            else:
                log.debug(f'Calling statement {item.statement.pretty_name}')
                self.proof_step.lean_code = lean_code
                # Update lean_file and call Lean server
                await self.servint.code_insert(statement.pretty_name,
                                               lean_code)

    async def __server_send_editor_lean(self):
        """
        Send the L∃∀N code written in the L∃∀N editor widget to the
        server interface.
        """
        await self.servint.code_set(_('Code from editor'),
                                    self.lean_editor.code_get())

    #########
    # Slots #
    #########

    @Slot()
    def empty_current_selection(self):
        """
        Clear current (user) selection of math. objects and properties.
        """

        for item in self.current_selection:
            item.mark_user_selected(False)
        self.current_selection = []
        if self.target_selected_by_default:
            self.ecw.target_wgt.mark_user_selected(self.target_selected)

    @Slot()
    def freeze(self, yes=True):
        """
        Freeze interface (inactive widgets, gray appearance, etc) if
        yes:
            - disable objects and properties;
            - disable all buttons;
        unfreeze it otherwise.

        :param yes: See above.
        """

        self.ecw.freeze(yes)
        self.toolbar.setEnabled(not yes)

    @Slot()
    def fireworks(self):
        """
        As of now,
        - display a dialog when the target is successfully solved,
        - replace the target by a message "No more goal"
        Note that the dialog is displayed only the first time the signal is
        triggered, thanks to the flag self.cqdf.
        """
        # TODO: make it a separate class

        # Display msg_box unless redoing or test mode
        # (Previously was: Display unless exercise already solved)
        # if not self.exercise_solved:
        if not self.proof_step.is_redo() and not self.test_mode:
            title = _('Target solved')
            text = _('The proof is complete!')
            msg_box = QMessageBox(parent=self)
            msg_box.setText(text)
            msg_box.setWindowTitle(title)
            button_ok = msg_box.addButton(_('Back to exercise'),
                                          QMessageBox.YesRole)
            button_change = msg_box.addButton(_('Change exercise'),
                                              QMessageBox.YesRole)
            button_change.clicked.connect(self.change_exercise)
            msg_box.exec()

        self.proof_step.no_more_goal = True
        # Artificially create a final proof_state by replacing target by a msg
        # (We do not get the final proof_state from Lean).
        proof_state = deepcopy(self.proof_step.proof_state)
        target = proof_state.goals[0].target
        target.math_type = MathObject(node="NO_MORE_GOAL",
                                      info={},
                                      children=[],
                                      )
        # Update proof_step and UI
        self.update_proof_state(proof_state)

        if not self.exercise_solved:
            self.exercise_solved = True
            if not self.test_mode:  # Save exercise for auto-test
                self.lean_file.save_exercise_for_autotest(self)

    @Slot(MathObjectWidgetItem)
    def process_context_click(self, item: MathObjectWidgetItem):
        """
        Add or remove item (item represents a math. object or property)
        from the current selection, depending on whether it was already
        selected or note.

        :item: The math. object or property user just clicked on.
        """

        # Once clicked, one does not want the item to remain visually
        # selected
        item.setSelected(False)
        # Un-select target
        self.ecw.target_wgt.mark_user_selected(False)
        self.target_selected = False

        if item not in self.current_selection:
            item.mark_user_selected(True)
            self.current_selection.append(item)
        else:
            item.mark_user_selected(False)
            self.current_selection.remove(item)

        if not self.current_selection and self.target_selected_by_default:
            # Target is automatically selected if current_selection is empty
            self.ecw.target_wgt.mark_user_selected(self.target_selected)

    @Slot()
    def process_target_click(self, event):
        """
        Select or un-select target. Current context selection is emptied.
        """

        self.target_selected = not self.target_selected
        self.ecw.target_wgt.mark_user_selected(self.target_selected)

        # Un-select context items
        self.empty_current_selection()

    @Slot()
    def __update_lean_editor(self):
        """
        Update the L∃∀N editor widget to that of the current virtual
        file L∃∀N code.
        """

        self.lean_editor.code_set(self.servint.lean_file.inner_contents)

    @Slot(ProofState)
    def update_proof_state(self, proofstate: ProofState):
        """
        Update self (attributes, interface) to the new proof state,
        which includes the new goal. This is also where self.proof_step is
        updated and stored both in the journal and in lean_file's history if
        this is adequate.

        :proofstate: The proofstate one wants to update self to.
        """

        # ─────────── Display msgs (no msg when undoing) ────────── #
        if not self.proof_step.is_history_move():
            self.statusBar.display_message(self.proof_step)
        elif self.proof_step.is_redo():
            self.statusBar.display_message(self.lean_file.current_proof_step)

        # ───────────── Store data ──────────── #
        # Store proof_state in proof_step
        self.proof_step.proof_state = proofstate

        # Store current proof_step in the lean_file (for logical memory)
        # and in the journal (for comprehensive memory)
        # We do NOT want to modify the attached context if we are moving in
        # history or recovering from an error.
        if not self.proof_step.is_history_move()\
                and not self.proof_step.is_error():
            # log.debug("Attaching proof_step to history")
            self.lean_file.state_info_attach(proof_step=self.proof_step)
        if not self.test_mode:
            self.journal.store(self.proof_step, self)

        # ─────────────── Update goals counters ─────────────── #
        delta = self.lean_file.current_number_of_goals \
                - self.lean_file.previous_number_of_goals
        if delta > 0:  # A new goal has appeared
            self.proof_step.total_goals_counter += delta
        elif delta < 0:  # A goal has been solved
            self.proof_step.current_goal_number -= delta
            if self.proof_step.current_goal_number and not self.test_mode \
                    and self.lean_file.current_number_of_goals \
                    and not self.proof_step.is_error() \
                    and not self.proof_step.is_undo():
                log.info(f"Current goal solved!")
                if delta == -1:
                    message = _('Current goal solved')
                else:  # Several goals solved at once ??
                    nb = str(-delta)
                    message = nb + ' ' + _('goals solved!')
                QMessageBox.information(self,
                                        '',
                                        message,
                                        QMessageBox.Ok
                                        )

        # ─────────────── End of proof_step ─────────────── #
        # Pass proof_step to displayed_proof_step, and create a new proof_step
        # with same goals data as logically previous proof step.
        # Note that we also keep the proof_state because it is needed by the
        # logical actions to compute the pertinent Lean code.
        self.displayed_proof_step = copy(self.proof_step)
        # LOGICAL proof_step is always in lean_file's history
        self.proof_step = ProofStep.next(self.lean_file.current_proof_step)

        self.proof_step_updated.emit()  # Received in auto_test

        # ─────────────── Update goal on ui ─────────────── #
        # if proofstate is not displayed_proof_state:
        #     self.update_goal(proofstate.goals[0])
        # else:
        #     self.ui_updated.emit()
        self.update_goal(proofstate.goals[0])

    @Slot(CodeForLean)
    def store_effective_code(self, effective_lean_code):
        self.proof_step.effective_code = effective_lean_code

