"""
Coordinator.py : coordination of ui and logics.

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 08 2021 (creation)
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

# TODO:
#  - Put UserActionStep as an attribute of emw, and fill it there.
#  Then store it in proof_step.
#  - Use Coordinator.action_queue to complete implementation of  implicit def
#  and auto_forall
#  - EMW should send abstract info (action instead of buttons,
#                                   ContextMathObjects instead of WidgetItems,
#                                   ...)

from functools import partial
import                logging
from typing import    Callable
import                qtrio
from copy import      copy, deepcopy


from PySide2.QtCore import ( QObject,
                             Signal,
                             Slot  )
from PySide2.QtWidgets import (QInputDialog,
                               QMessageBox)


from deaduction.dui.primitives      import ButtonsDialog
from deaduction.dui.stages.exercise import ExerciseMainWindow

from deaduction.pylib.server.exceptions import  FailedRequestError

from deaduction.pylib.server        import ServerInterface

from deaduction.pylib.coursedata        import (Statement,
                                                Exercise,
                                                Definition,
                                                Theorem,
                                                AutoStep)

from deaduction.pylib.mathobj           import (MathObject,
                                                PatternMathObject,
                                                MissingImplicitDefinition,
                                                Goal,
                                                ProofState,
                                                ProofStep)
from deaduction.pylib.actions           import (generic,
                                                InputType,
                                                CodeForLean,
                                                MissingParametersError,
                                                WrongUserInput)

from deaduction.pylib.memory            import Journal

log = logging.getLogger(__name__)
global _


@classmethod
class UserActionStep:
    """
    A class for storing usr actions for one step.
    """
    selection      = None  # [MathObject]
    user_input     = None  # [str]
    button         = None  # ActionButton or str, e.g. "history_undo".
    statement_item = None  # StatementsTreeWidgetItem


class Coordinator(QObject):
    """
    Coordinate UI (ExerciseMainWindow), logical actions, and Lean server.

    Info needed by ExerciseMainWindow:
    - For init,
        - list of buttons,
        - list of statements, with initial proof states.

    - For updating,
        - goal = a list of ContextMathObjects, and a target.
        - tags history at beginning / at end (for toolbar)
        - tag no_goal
        - msgs for StatusBar
        - delta_goal_count for displaying "goal solved" msg.
        - lean_file content for the lean_editor console.

    For the moment, much info is passed through proof_step and lean_file.
    """

    proof_step_updated              = Signal()

    def __init__(self, exercise, servint):
        super().__init__()
        self.exercise: Exercise       = exercise
        self.servint: ServerInterface = servint
        self.emw = ExerciseMainWindow(exercise, lean_file=None)
        # Lean_file will be set when starting server_task
        self.emw.close_coordinator = self.closeEvent

        # self.current_action_step            = None
        # self.action_queue: [UserActionStep] = None

        self.proof_step                     = ProofStep()
        self.journal                        = Journal()

        # Flags
        self.exercise_solved                = False
        self.test_mode                      = False

        # Initialization
        self.__connect_signals()
        self.__initialize_exercise()

    ##############
    # Properties #
    ##############

    # TODO move to EMW?
    @property
    def lean_file(self):
        return self.servint.lean_file

    @property
    def ecw(self):
        return self.emw.ecw

    @property
    def proof_outline_window(self):
        return self.emw.proof_outline_window

    @property
    def toolbar(self):
        return self.emw.toolbar

    @property
    def statusBar(self):
        return self.emw.statusBar

    @property
    def lean_editor(self):
        return self.emw.lean_editor

    @property
    def displayed_proof_step(self):
        return self.emw.displayed_proof_step

    @property
    def action_triggered(self):
        return self.emw.action_triggered

    @property
    def statement_triggered(self):
        return self.emw.statement_triggered

    @property
    def apply_math_object_triggered(self):
        return self.emw.apply_math_object_triggered

    @property
    def double_clicked_item(self):
        return self.emw.double_clicked_item

    @property
    def current_selection(self):
        return self.emw.current_selection

    @property
    def current_selection_as_mathobjects(self):
        return self.emw.current_selection_as_mathobjects

    @property
    def target_selected(self):
        return self.emw.target_selected

    #######################
    #######################
    # Init /close methods #
    #######################
    #######################

    def __connect_signals(self):
        """
        Connect all signals. Called at init and sever update.
        """
        # self.servint.proof_state_change.connect(self.update_proof_state)
        self.servint.lean_file_changed.connect(self.emw.update_lean_editor)
        # self.servint.proof_no_goals.connect(self.fireworks)
        self.servint.effective_code_received.connect(
            self.process_effective_code)

        # self.servint.failed_request_errors.connect(
        #                                    self.process_failed_request_error)
        self.servint.lean_response.connect(self.process_lean_response)

    def __initialize_exercise(self):
        """
        Set initial proof states of exercise and all statements,
        and call self.start_server_task.
        """
        log.debug("Initializing exercise")

        # Try to display initial proof state prior to anything
        proof_state = self.exercise.initial_proof_state
        if proof_state:
            goal = proof_state.goals[0]
            self.emw.ecw.update_goal(goal, 1, 1)

        # When exercise will be set, ui will be updated, and the following
        # will call self.start_server_task
        self.servint.exercise_set.connect(self.start_server_task)

        # Set exercise
        self.servint.server_queue.add_task(self.servint.set_exercise,
                                           self.exercise,
                                           on_top=True)

        # Missing initial proof states?
        course = self.exercise.course
        statements = [st for st in self.exercise.available_statements
                      if not st.initial_proof_state]
        if statements:
            # Just in case initial proof states have not been received yet
            self.servint.initial_proof_state_set.connect(
                                self.emw.ecw.statements_tree.update_tooltips)
            self.servint.initial_proof_state_set.connect(
                                self.set_definitions_for_implicit_use)

            self.servint.set_statements(course, statements)

        # Implicit definitions
        self.set_definitions_for_implicit_use()

    @Slot()
    def set_definitions_for_implicit_use(self):
        exercise = self.exercise
        definitions = exercise.definitions_for_implicit_use
        log.debug(f"{len(definitions)} definition(s) set for implicit use")
        PatternMathObject.set_definitions_for_implicit_use(definitions)
        log.debug(f"{len(MathObject.definition_patterns)} implicit "
                  f"definitions in MathObject list")


    def closeEvent(self):
        log.info("Closing Coordinator")

        self.disconnect_signals()

        # Save journal
        if not self.test_mode:
            self.journal.save_exercise_with_proof_steps(emw=self)
        # Save new initial proof states, if any
        self.exercise.course.save_initial_proof_states()
        # FIXME:  cancel server_task
        # if self.__server_task_scope:
        #     self.__server_task_scope.cancel()

    def disconnect_signals(self):
        """
        This method is called at closing. It is VERY important: without it,
        servint signals will still be connected to methods concerning
        the previous exercise.
        """
        self.servint.lean_file_changed.disconnect()
        self.servint.effective_code_received.disconnect()
        self.servint.exercise_set.disconnect()
        self.servint.lean_response.disconnect()

    ######################################################
    ######################################################
    # ─────────────────── Server task ────────────────── #
    ######################################################
    ######################################################

    @Slot()
    def start_server_task(self):
        self.emw.lean_file = self.servint.lean_file
        self.servint.nursery.start_soon(self.server_task,
                                        name="Server task")

    async def server_task(self):
        """
        This method handles sending user data and actions to the server
        interface (self.servint). It listens to signals and calls
        specific methods for those signals accordingly. Actions are then
        sent to the ServerQueue of ServerInterface.
        This method is called at initialisation of Coordinator.
        The user actions are stored in self.proof_step.
        """

        log.info("Starting server task")

        self.emw.freeze(False)
        async with qtrio.enter_emissions_channel(
                signals=[self.lean_editor.editor_send_lean,
                         self.toolbar.redo_action.triggered,
                         self.toolbar.undo_action.triggered,
                         self.toolbar.rewind.triggered,
                         self.proof_outline_window.history_goto,
                         self.action_triggered,
                         self.statement_triggered,
                         self.apply_math_object_triggered]) as emissions:
            async for emission in emissions.channel:
                self.statusBar.erase()
                self.emw.freeze(True)
                # DO NOT forget to unfreeze at th end. TODO: add timeout
                log.debug("Emission in the server_task channel")
                ########################
                # History move actions #
                ########################
                if emission.is_from(self.toolbar.redo_action.triggered)\
                        and not self.lean_file.history_at_end:
                    # No need to call self.update_goal, this emits the
                    # signal proof_state_change of which
                    # self.update_goal is a slot.
                    # The UI simulate the redone step if possible.
                    self.proof_step.button = 'history_redo'
                    proof_step = self.lean_file.next_proof_step
                    if proof_step:
                        await self.emw.simulate(proof_step)
                    self.servint.server_queue.add_task(
                                                    self.servint.history_redo)

                elif emission.is_from(self.toolbar.undo_action.triggered):
                    self.proof_step.button = 'history_undo'
                    self.servint.server_queue.add_task(
                                                    self.servint.history_undo)

                elif emission.is_from(self.toolbar.rewind.triggered):
                    self.proof_step.button = 'history_rewind'
                    self.servint.server_queue.add_task(
                                                self.servint.history_rewind)

                elif emission.is_from(self.proof_outline_window.history_goto):
                    history_nb = emission.args[0]
                    self.proof_step.button = 'history_goto'
                    self.servint.server_queue.add_task(
                                        self.servint.history_goto, history_nb)
                ########################
                # Code to Lean actions #
                ########################
                elif emission.is_from(self.lean_editor.editor_send_lean):
                    self.__server_send_editor_lean()

                elif emission.is_from(self.action_triggered):
                    # emission.args[0] is the ActionButton triggered by user
                    button = emission.args[0]
                    self.proof_step.button = button
                    if button == self.ecw.action_apply_button \
                            and self.double_clicked_item:
                        # TODO: move this to ecw
                        # Make sure item is marked and added to selection
                        item = self.double_clicked_item
                        if item in self.current_selection:
                            self.current_selection.remove(item)
                        self.current_selection.append(item)  # Item is last
                        self.emw.double_clicked_item = None
                    self.__server_call_action(emission.args[0])

                elif emission.is_from(self.statement_triggered):
                    # emission.args[0] is the StatementTreeWidgetItem
                    # triggered by user
                    if hasattr(emission.args[0], 'statement'):
                        self.proof_step.statement_item = emission.args[0]
                    self.__server_call_statement(emission.args[0])

                elif emission.is_from(self.apply_math_object_triggered):
                    # Fixme: put in EMW
                    self.emw.double_clicked_item = emission.args[0]
                    # Emulate click on 'apply' button:
                    self.ecw.action_apply_button.animateClick(msec=500)

    ################################################
    # Actions that send code to Lean (via servint) #
    ################################################
    def __server_call_action(self,
                                   action_btn,  # ActionButton
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
        if auto_selection:  # For auto-test
            selection = auto_selection
            self.proof_step.selection = selection
            target_selected = True if not selection else False
        else:
            selection = self.current_selection_as_mathobjects
            self.proof_step.selection = selection
            target_selected = self.emw.target_selected
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
                        target_selected=target_selected)
                else:
                    lean_code = action.run(
                        self.proof_step,
                        selection,
                        user_input,
                        target_selected=target_selected)

            except MissingParametersError as e:
                if e.input_type == InputType.Text:
                    # TODO: move this into EMW methods
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
                    self.unfreeze()
                    break

            except WrongUserInput as error:
                self.proof_step.user_input = user_input
                self.process_wrong_user_input(error)
                break

            # New: implicit use of definition
            except MissingImplicitDefinition as mid:
                definition = mid.definition
                math_object = mid.math_object
                rewritten_math_object = mid.rewritten_math_object
                selection_rw = selection
                index = math_object.find_in(selection)
                if index is not None:
                    selection_rw = [selection[index]]
                log.debug(f"Implicit use of definition "
                          f"{definition.pretty_name} in ")
                log.debug(f"{math_object.to_display()} -> ")
                log.debug(f"{rewritten_math_object.to_display()}")
                lean_code = generic.action_definition(self.proof_step,
                                                      selection_rw,
                                                      definition,
                                                      target_selected)
                self.servint.server_queue.add_task(
                                                    self.servint.code_insert,
                                                    definition.pretty_name,
                                                    lean_code)
                # TODO: add action in self.action_queue
                break

            else:
                self.proof_step.lean_code = lean_code
                self.proof_step.user_input = user_input
                # Update lean_file and call Lean server
                self.servint.server_queue.add_task(
                                                    self.servint.code_insert,
                                                    action.symbol,
                                                    lean_code)
                break

    def __server_call_statement(self,
                                      item,  # StatementsTreeWidgetItem
                                      auto_selection=None):
        """
        This function is called when the user clicks on a Statement he wants to
        apply. The statement can be either a Definition or a Theorem. the code
        is then inserted to the server.
        """
        if auto_selection:
            selection = auto_selection
            self.proof_step.selection = selection
            target_selected = True if not selection else False
        else:
            selection = self.current_selection_as_mathobjects
            self.proof_step.selection = selection
            target_selected = self.emw.target_selected

        # Do nothing if user clicks on a node
        # FIXME: filter this, and UI actions, in EMW
        if item.is_node():
            return
        try:
            item.setSelected(False)
            statement = item.statement

            if isinstance(statement, Definition):
                lean_code = generic.action_definition(
                    self.proof_step,
                    selection,
                    statement,
                    target_selected)
            elif isinstance(statement, Theorem):
                lean_code = generic.action_theorem(
                    self.proof_step,
                    selection,
                    statement,
                    target_selected)

        except WrongUserInput as error:
            self.process_wrong_user_input(error)
            # self.emw.empty_current_selection()
            # self.update_proof_state(self.displayed_proof_step.proof_state)

        else:
            log.debug(f'Calling statement {item.statement.pretty_name}')
            self.proof_step.lean_code = lean_code
            # Update lean_file and call Lean server
            self.servint.server_queue.add_task(
                                                self.servint.code_insert,
                                                statement.pretty_name,
                                                lean_code)

    def __server_send_editor_lean(self):
        """
        Send the L∃∀N code written in the L∃∀N editor widget to the
        server interface.
        """
        self.servint.server_queue.add_task(
                                self.servint.code_set,
                                _('Code from editor'),
                                self.lean_editor.code_get())

    #########################
    #########################
    # Process Lean response #
    #########################
    #########################

    def unfreeze(self):
        # TODO: put this in EMW

        if self.lean_file.current_proof_step \
                and not self.lean_file.current_proof_step.no_more_goal:
            self.emw.freeze(False)
        else:  # If no more goals, disable actions but enable toolbar
            self.emw.ecw.freeze(True)
            self.emw.toolbar.setEnabled(True)
        at_beginning = self.servint.lean_file.history_at_beginning
        at_end = self.servint.lean_file.history_at_end

        self.emw.history_button_unfreeze(at_beginning, at_end)

    @Slot(CodeForLean)
    def process_effective_code(self, effective_lean_code):
        self.proof_step.effective_code = effective_lean_code
        self.servint.history_replace(effective_lean_code)

    @Slot()
    def process_failed_request_error(self, errors):
        """
        Note that history_delete will be called.
        """
        self.proof_step.error_type = 2
        lean_code = self.proof_step.lean_code
        if lean_code.error_msg:
            self.proof_step.error_msg = lean_code.error_msg
        else:
            self.proof_step.error_msg = _('Error')

        details = ""
        for error in errors:
            details += "\n" + error.text
        log.debug(f"Lean errors, details: {details}")

    def process_wrong_user_input(self, error):
        self.proof_step.error_type = 1
        self.proof_step.error_msg = error.message

        self.update_proof_step()

        self.emw.process_wrong_user_input()
        self.unfreeze()
        self.emw.update_goal(None)

    @Slot()
    def set_fireworks(self):
        """
        As of now,
        - display a dialog when the target is successfully solved,
        - replace the target by a message "No more goal".
        """
        # Display msg_box unless redoing /moving or test mode
        # TODO: move this part to EMW
        if not self.proof_step.is_redo() and not self.proof_step.is_goto()\
                and not self.test_mode:
            title = _('Target solved')
            text = _('The proof is complete!')
            msg_box = QMessageBox(parent=self.emw)
            msg_box.setText(text)
            msg_box.setWindowTitle(title)
            button_ok = msg_box.addButton(_('Back to exercise'),
                                          QMessageBox.YesRole)
            button_change = msg_box.addButton(_('Change exercise'),
                                              QMessageBox.YesRole)
            button_change.clicked.connect(self.emw.change_exercise)
            msg_box.exec_()

        self.proof_step.no_more_goal = True
        self.proof_step.new_goals = []
        # Artificially create a final proof_state by replacing target by a msg
        # (We do not get the final proof_state from Lean).
        proof_state = deepcopy(self.proof_step.proof_state)
        target = proof_state.goals[0].target
        target.math_type = MathObject(node="NO_MORE_GOAL",
                                      info={},
                                      children=[],
                                      math_type=None)

        return proof_state

    @Slot()
    def process_lean_response(self,
                              no_more_goals: bool,
                              analysis: tuple,
                              errors: list):
        """
        This method processes Lean response after a request, and is a slot
        of a signal emitted by self.servint when all info have been received.
        There are exactly three mutually exclusive possibilities:
        (1) Proof is complete,
        (2) The request has failed,
        (3) The request has succeeded but proof is not complete.

        :param no_more_goals: True if no_more_goal: proof is complete!
        :param analysis: (hypo_analysis, targets_analysis),
                         = info to construct new proof_state
        :param errors: list of errors, if non-empty then request has failed.
        """
        log.info("Processing Lean's response")
        if no_more_goals:
            log.info("  -> proof completed!")
            proof_state = self.set_fireworks()

        elif errors:
            log.info("  -> errors")
            self.process_failed_request_error(errors)
            # Abort and go back to last goal
            self.servint.server_queue.add_task(self.servint.history_delete)
            # Process_lean_response will be called again after deleting
            return

        else:  # Generic step
            hypo_analysis, targets_analysis = analysis
            proof_state = ProofState.from_lean_data(hypo_analysis,
                                                    targets_analysis)
            log.debug("  -> computing new ProofState")
            self.lean_file.state_info_attach(ProofState=proof_state)

        # No need to update if errors or recovering from errors
        if not self.proof_step.is_error():
            self.proof_step.proof_state = proof_state
            if not self.proof_step.is_history_move():
                log.debug("     Storing proof step in lean_file info")
                self.lean_file.state_info_attach(proof_step=self.proof_step)

            # Check for new goals
            delta = self.lean_file.delta_goals_count
            self.proof_step.delta_goals_count = delta
            self.proof_step.update_goals()

            # Debug
            log.debug(f"    Target_idx: {self.lean_file.target_idx}")
            log.debug("     Proof nodes:")
            for he in self.lean_file.history:
                proof_nodes = he.misc_info.get('proof_step').proof_nodes
                log.debug([pf.txt for pf in proof_nodes])

        # Update proof_step
        self.update_proof_step()

        # Update UI
        self.unfreeze()
        if self.proof_step.is_error():
            self.emw.update_goal(None)
        else:
            self.emw.update_goal(proof_state.goals[0])

    def update_proof_step(self):
        """
        Store proof_step and creat next proof_step.
        This is called for every user action, including errors and history
        moves.
        """
        # Store journal and auto_step
        if not self.test_mode:
            self.journal.store(self.proof_step, self)
            self.proof_step.auto_step = AutoStep.from_proof_step(
                                                            self.proof_step,
                                                            emw=self.emw)

        # Create next proof_step
        self.emw.displayed_proof_step = copy(self.proof_step)
        self.proof_step = ProofStep.next_(self.lean_file.current_proof_step,
                                          self.lean_file.target_idx)
        self.proof_step_updated.emit()  # Received in auto_test

        # Saving for auto-test if proof complete
        if self.proof_step.no_more_goal and not self.exercise_solved:
            self.exercise_solved = True
            if not self.test_mode:
                self.lean_file.save_exercise_for_autotest(self)


