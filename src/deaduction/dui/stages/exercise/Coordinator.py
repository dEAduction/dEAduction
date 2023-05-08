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
    with d∃∀duction.  If not, see <https://www.gnu.org/licenses/>.
"""

# TODO:
#  - EMW should send abstract info (action instead of buttons,
#                                   ContextMathObjects instead of WidgetItems,
#                                   ...)

import                logging
import                qtrio
import trio
from copy import      copy, deepcopy
from typing import Optional

from PySide2.QtCore import ( QObject,
                             Signal,
                             Slot,
                             QTimer)
from PySide2.QtWidgets import (QInputDialog,
                               QMessageBox)

# Configs, utils
import deaduction.pylib.config.dirs as          cdirs
import deaduction.pylib.config.vars as          cvars
from deaduction.pylib.utils.filesystem import   check_dir

# DUI
from deaduction.dui.primitives import           ButtonsDialog
from deaduction.dui.stages.exercise import      ExerciseMainWindow
from deaduction.dui.elements import             ActionButton

# Server
from deaduction.pylib.server import             ServerInterface, Task

from deaduction.pylib.utils import save_object

# Maths
from deaduction.pylib.coursedata import        (Exercise,
                                                Definition,
                                                Theorem,
                                                UserAction,
                                                AutoStep)

from deaduction.pylib.mathobj import           (MathObject,
                                                DragNDrop,
                                                ContextMathObject)
from deaduction.pylib.proof_state import       Goal  # LeanResponse
from deaduction.pylib.proof_step import        ProofStep
from deaduction.pylib.proof_tree import        ProofTree

from deaduction.pylib.actions           import (generic,
                                                InputType,
                                                CodeForLean,
                                                MissingParametersError,
                                                WrongUserInput,
                                                drag_n_drop)

# Import AFTER coursedata and mathobj, beware circular imports!
from deaduction.pylib.pattern_math_obj import  (PatternMathObject,
                                                DefinitionMathObject)

# Just for import
from deaduction.pylib.math_display.new_display import to_display

from deaduction.pylib.memory            import Journal

log = logging.getLogger(__name__)
global _


class Coordinator(QObject):
    """
    Coordinate UI (ExerciseMainWindow), logical actions, and Lean server.
    The main attributes are
    - exercise: Exercise
    - servint: ServerInerface, a high level interface with Lean server
    - emw: ExerceiseMainWindow

    Note aso the proof_step attribute: this records all user actions,
    the Lean code that they generates, and the responses from the lean server.

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

    proof_step_updated = Signal()  # Listened by test_launcher (for testing)
    close_server_task  = Signal()  # Send by self.closeEvent
    frozen             = Signal()
    unfrozen           = Signal()

    def __init__(self, exercise, servint):
        super().__init__()
        self.cvars_to_be_restored = exercise.update_cvars_from_metadata()
        self.exercise: Exercise       = exercise
        self.servint: ServerInterface = servint
        self.last_servint_task = None

        # Exercise main window
        self.emw = ExerciseMainWindow(exercise)
        self.emw.statusBar.display_initializing_bar()
        self.emw.close_coordinator = self.closeEvent

        # Information
        self.proof_step: Optional[ProofStep]          = None  # Set later
        self.proof_tree: Optional[ProofTree]          = None
        self.previous_proof_step: Optional[ProofStep] = None
        self.journal                                  = Journal()
        self.lean_code_sent: Optional[CodeForLean]          = None

        # Flags
        self.exercise_solved                = False
        self.test_mode                      = False
        self.history_mode                   = exercise.is_history()
        self.server_task_started            = trio.Event()
        self.server_task_closed             = trio.Event()
        self.initial_proof_states_set = trio.Event()

        self.stop_button_will_stop_server   = False

        # Initialization
        self.is_frozen = False
        self.__connect_signals()
        self.__initialize_exercise()
        # log.debug(f"Selected style: {self.emw.ecw.target_wgt.selected_style}")
    ######################
    ######################
    # Init/close methods #
    ######################
    ######################

    def __connect_signals(self):
        """
        Connect all signals. Called at init.
        """
        self.servint.lean_file_changed.connect(self.emw.update_lean_editor)
        # self.servint.effective_code_received.connect(
        #                                         self.process_effective_code)
        self.servint.lean_response.connect(self.process_lean_response)
        # self.emw.cancel_server.connect(self.cancel_server)

    def __initialize_exercise(self):
        """
        Set initial proof states of exercise and all statements.
        Note that server_task will be started by the process_lean_response
        method that will be called after the self.servint.set_exercise.
        """
        log.debug("Initializing exercise")

        # Try to display initial proof state of self.exercise prior to anything
        #  (so that user may start thinking, even if UI stay frozen for a
        #  while.)
        self.proof_tree = ProofTree()
        self.emw.proof_tree_controller.set_proof_tree(self.proof_tree)
        self.emw.set_msgs_for_status_bar(self.proof_tree.current_proof_msg)
        self.proof_step = ProofStep()
        proof_state = self.exercise.initial_proof_state
        if proof_state:
            goal = proof_state.goals[0]
            # goal.name_bound_vars()
            self.emw.ecw.update_goal(goal, [])

        # Set exercise. In particular, this will initialize servint.lean_file.
        task = Task(fct=self.servint.set_exercise,
                    kwargs={'proof_step': self.proof_step,
                            'exercise': self.exercise,
                            'on_top': True})
        self.send_task_to_server(task)

        # Set initial proof states for all statements
        # (Already done if start_coex was launched, but useful otherwise:)
        self.exercise.course.load_initial_proof_states()
        self.set_initial_proof_states()

        # Set implicit definitions
        # Initialize the following lists to erase lists from previous exercise
        MathObject.implicit_definitions = []
        MathObject.definition_patterns = []
        self.set_math_object_definitions()
        self.set_definitions_for_implicit_use()

    def set_initial_proof_states(self):
        """
        If some ips are missing, ask servint for them and connect signal to
        update information when ips are set.
        """
        statements = [st for st in self.exercise.available_statements
                      if not st.initial_proof_state]
        if statements:
            self.servint.initial_proof_state_set.connect(
                                self.check_initial_proof_states_set)
            self.servint.set_statements(self.exercise.course, statements)
        else:
            log.info("All initial proof states set")
            self.initial_proof_states_set.set()

    @Slot()
    def check_initial_proof_states_set(self):
        """
        This is called by servint each time a new initial_proof_state is
        set, if the signal initial_proof_state_set is connected.
        The method tries to use the new ips to set implicit definitions and
        to set tooltips.
        Then it checks if there are ips still missing, and if not,
        disconnect signal.
        """
        self.set_definitions_for_implicit_use()
        # self.emw.ecw.statements_tree.update_tooltips()

        statements = [st for st in self.exercise.available_statements
                      if not st.initial_proof_state]
        if not statements:
            log.info("All initial proof states set")
            self.initial_proof_states_set.set()
            self.servint.initial_proof_state_set.disconnect()

    def set_math_object_definitions(self):
        definitions = self.exercise.definitions
        DefinitionMathObject.set_definitions(definitions)

    @Slot()
    def set_definitions_for_implicit_use(self):
        """
        Set up definitions that will the user may use implicitly.
        For instance, say definition.inclusion is marked for implicit use in
        the lean exercise file:
            lemma definition.inclusion {A B : set X} :
            A ⊆ B ↔ ∀ {x:X}, x ∈ A → x ∈ B :=
            /- dEAduction
            ImplicitUse
                True
            -/
        Then the user must be able to apply button '∀' on the property 'A ⊆ B'
        without unfolding the definition.

        Note that deaduction needs the initial_proof_state of a given
        definition to be able to add it in the implicit use list. This is
        why the signal self.servint.initial_proof_state_set is connected to
        this method's slot: each time new initial_proof_states are set up in
        servint, this method is called.

        See PatternMathObject for more details.
        """
        exercise = self.exercise
        definitions = exercise.definitions_for_implicit_use
        definitions_with_ips = [st for st in definitions if
                                st.initial_proof_state]
        if len(definitions_with_ips) == len(MathObject.definition_patterns):
            # All definitions already set up
            # Beware that MathObject.definition_patterns does not come from
            # previous exercise
            return
        log.debug(f"Found {len(definitions)} definition(s) for implicit "
                  f"use...")
        PatternMathObject.set_definitions_for_implicit_use(definitions)
        log.debug(f"...set {len(MathObject.definition_patterns)} implicit "
                  f"definitions")
        # log.debug("Metavar_objects list (nb, name, type):")
        loc_csts = PatternMathObject.loc_csts_for_metavars
        # log.debug([(idx+1, loc_csts[idx].to_display(),
        #             loc_csts[idx].math_type.to_display(),
        #             " / ", PatternMathObject.metavars_csts[
        #                 idx].math_type.to_display())
        #            for idx in range(len(loc_csts))])

        # Just in case of deletion:
        self.emw.ecw.statements_tree.update_tooltips()
        # try:
        #     self.emw.ecw.statements_tree.update_tooltips()
        # except RuntimeError:
        #     log.warning(f"Runtime error (StatementsTreeWidgetItem deleted?)")

    def save_exercise_for_autotest(self):
        """
        This method fills self.exercise's attribute refined_auto_step
        by retrieving the list of proof_step.auto_step from the lean_file,
        and save the resulting exercise object in a pkl file for future
        testing.
        """
        save = cvars.get('functionality.save_solved_exercises_for_autotest',
                         False)
        if not save:
            return

        auto_steps = [entry.misc_info.get("proof_step").auto_step
                      for entry in self.lean_file.history]
        auto_steps = [step for step in auto_steps if step is not None]

        exercise = self.exercise
        exercise.refined_auto_steps = auto_steps
        filename = ('test_' + exercise.lean_short_name).replace('.', '_') \
            + '.pkl'
        file_path = cdirs.test_exercises / filename
        check_dir(cdirs.test_exercises, create=True)

        total_string = 'AutoTest\n'
        for step in auto_steps:
            total_string += '    ' + step.raw_string + ',\n'
        print(total_string)

        log.debug(f"Saving auto_steps in {file_path}")

        save_object(exercise, file_path)
        # with open(file_path, mode='wb') as output:
        #     dump(exercise, output, HIGHEST_PROTOCOL)

    def disconnect_signals(self):
        """
        This method is called at closing. It may be important: without it,
        servint signals will still be connected to methods concerning
        the previous exercise.
        """
        if self.servint:
            # It seems that sometimes signals are already deleted
            # try:
            #     self.servint.effective_code_received.disconnect()
            # except RuntimeError:
            #     log.debug("(Impossible to disconnect signal effective code "
            #               "received)")
            try:
                self.servint.lean_response.disconnect()
            except RuntimeError:
                log.debug("(Impossible to disconnect signal lean response)")
            if self.emw:  # This signal is connected to some emw method
                try:
                    self.servint.lean_file_changed.disconnect()
                except RuntimeError:
                    log.debug("(Impossible to disconnect signal lean file "
                              "changed)")

    def closeEvent(self):
        """
        Called at closing, and when closing ExerciseMainWindow.
        """
        log.info("Closing Coordinator")
        # continue_ = input("Closing Coordinator?")  # FIXME: debugging

        # try:
        #     self.disconnect_signals()
        # except RuntimeError:
        #     # It seems that sometimes signals are already deleted
        #     log.debug("(Impossible to disconnect signals)")

        self.disconnect_signals()

        # key = 'functionality.save_history_of_solved_exercises'
        # save_history = cvars.get(key, False)
        if not self.test_mode and not self.history_mode:
            # Save journal
            self.journal.save_exercise_with_proof_steps(emw=self)
            # Save new initial proof states, if any
            self.exercise.course.save_initial_proof_states()
            # Save exercise for autotest
            # if save_history:
            #     # TODO: compute list of pertinent ProofSteps
            #     #  (without history moves)
            #     #  And turn them to AutoSteps, then to strings.
            #     self.exercise.save_with_auto_steps()

        # Emit close_server_task signal and wait for effect
        # tasks = self.servint.nursery.child_tasks
        # log.debug(f"{len(tasks)} nursery tasks:")
        # log.debug([task.name for task in tasks])
        # log.debug("Closing server task")
        self.close_server_task.emit()
        if self.cvars_to_be_restored:
            cvars.update(self.cvars_to_be_restored)
        # self.deleteLater()  FIXME: needed ??

    ##############
    # Properties #
    ##############

    @property
    def action_button_names(self) -> [str]:
        # buttons = self.emw.ecw.actions_buttons
        # return [button.name for button in buttons]
        buttons = ActionButton.from_name.keys()
        return buttons

    @property
    def code_insert(self):
        return self.servint.code_insert

    @property
    def lean_file(self):
        return self.servint.lean_file

    @property
    def history_nb(self):
        return self.lean_file.target_idx

    # @property
    # def server_queue(self):
    #     return self.servint.server_queue

    @property
    def nursery(self):
        return self.servint.nursery

    @property
    def logically_previous_proof_step(self):
        """
        The previous proof step in the logical order is always stored in the
        previous entry of lean_file's history. This is NOT the proof step
        that was previously displayed by the ui in case of history undo or
        rewind (which is stored in self.displayed_proof_step), or in case of
        error.
        """
        if self.lean_file:
            return self.lean_file.previous_proof_step
        else:
            return None

    @property
    def ecw(self):
        return self.emw.ecw

    @property
    def proof_outline_window(self):
        return self.emw.proof_outline_window

    @property
    def toolbar(self):
        return self.emw.exercise_toolbar

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
    def statement_dropped(self):
        return self.emw.statement_dropped

    @property
    def math_object_dropped(self):
        return self.emw.math_object_dropped

    # @property
    # def apply_math_object_triggered(self):
    #     return self.emw.apply_math_object_triggered

    # @property
    # def double_clicked_item(self):
    #     return self.emw.double_clicked_item

    @property
    def current_selection(self):
        return self.emw.current_selection

    @property
    def current_selection_as_mathobjects(self):
        return self.emw.current_selection_as_mathobjects

    @property
    def target_selected(self):
        return self.emw.target_selected

    ######################################################
    ######################################################
    # ─────────────────── Server task ────────────────── #
    ######################################################
    ######################################################

    async def restart_lean_server(self):
        log.debug("Stopping Lean server...")
        # with trio.move_on_after(10):
        #     await self.servint.file_invalidated.wait()
        await self.servint.secured_stop()
        log.info("...stopped!")
        await self.servint.start()
        log.info("Lean server started")

    def stop_button_will_cancel_task(self):
        self.stop_button_will_stop_server = False

    async def stop(self):
        """
        This method is called when usr push the 'stop' button.
        """
        if self.servint:
            task = self.last_servint_task
            if task.status != "done":
                log.info(f"Trying to cancel last task (status {task.status})")
                self.servint.cancel_task(task)
                log.debug(f"(new status: {task.status})")
            elif self.stop_button_will_stop_server:
                await self.restart_lean_server()
                msg = _("Server restarted")
                self.statusBar.show_tmp_msg(msg)

            else:
                msg = _("No action to be cancelled, press again to restart "
                        "server")
                # msg = _("No action to be cancelled")
                # bar_msg = self.statusBar.messageWidget.text()
                # FIXME: bar_msg always empty?? REMOVE FOLLOWING LINE:
                # await self.restart_lean_server()
                self.stop_button_will_stop_server = True
                QTimer.singleShot(3000, self.stop_button_will_cancel_task)
                self.statusBar.show_tmp_msg(msg, duration=3000)

    def send_task_to_server(self, task: Task):
        self.last_servint_task = task
        self.servint.add_task(task)

    def start_server_task(self):
        """
        A front end for starting the async server_task method,
        which is called by self.process_lean_response at first call.
        """
        self.emw.lean_file = self.servint.lean_file
        self.servint.nursery.start_soon(self.server_task,
                                        name="Server task")

    async def server_task(self):
        """
        This method handles sending user data and actions to the server
        interface (self.servint). It listens to signals from self.emw and calls
        specific methods for those signals accordingly. Actions are then
        sent to the ServerQueue of ServerInterface.
        All user actions are stored in self.proof_step.
        """

        log.info("Starting server task")

        async with qtrio.enter_emissions_channel(
                signals=[self.lean_editor.editor_send_lean,
                         self.toolbar.redo_action.triggered,
                         self.toolbar.undo_action.triggered,
                         self.toolbar.rewind.triggered,
                         self.toolbar.go_to_end.triggered,
                         self.proof_outline_window.history_goto,
                         self.action_triggered,
                         self.statement_triggered,
                         self.statement_dropped,
                         self.math_object_dropped,
                         self.emw.stop,
                         # self.apply_math_object_triggered,
                         self.close_server_task]) as emissions:

            self.server_task_started.set()
            async for emission in emissions.channel:
                ###########
                # Closing #
                ###########
                log.debug(f"Emission in the server_task channel")
                if emission.is_from(self.close_server_task):
                    log.info("    -> Close server_Task...")
                    self.server_task_closed.set()
                    await emissions.aclose() # FIXME!!!! (for testing)
                    log.info("            ...closed!")
                    break

                self.statusBar.erase()
                self.freeze()  # DO NOT forget to unfreeze at the end.

                ########################
                # History move actions #
                ########################
                if emission.is_from(self.toolbar.redo_action.triggered)\
                        and not self.lean_file.history_at_end:
                    self.proof_step.button_name = 'history_redo'
                    proof_step = self.lean_file.next_proof_step
                    if proof_step:
                        await self.emw.simulate_proof_step(proof_step)
                    self.history_redo()

                elif emission.is_from(self.toolbar.undo_action.triggered):
                    self.proof_step.button_name = 'history_undo'
                    self.history_undo()

                elif emission.is_from(self.toolbar.rewind.triggered):
                    self.proof_step.button_name = 'history_rewind'
                    self.history_rewind()

                elif emission.is_from(self.toolbar.go_to_end.triggered):
                    self.proof_step.button_name = 'history_go_to_end'
                    self.history_go_to_end()

                elif emission.is_from(self.proof_outline_window.history_goto):
                    history_nb = emission.args[0]
                    if history_nb != self.history_nb:
                        self.proof_step.button_name = 'history_goto'
                        # add_task(self.servint.history_goto, history_nb)
                        self.history_goto(history_nb)
                    else:
                        self.unfreeze()
                ######################
                # Stop action/server #
                ######################
                elif emission.is_from(self.emw.stop):
                    await self.stop()
                    self.unfreeze()

                ########################
                # Code to Lean actions #
                ########################
                elif emission.is_from(self.lean_editor.editor_send_lean):
                    self.__server_send_editor_lean()

                elif emission.is_from(self.action_triggered):
                    button = emission.args[0]  # ActionButton triggered by user
                    self.proof_step.button_name = button.name
                    self.__server_call_action(emission.args[0])

                elif emission.is_from(self.statement_triggered):
                    # emission.args[0] is StatementTreeWidgetItem
                    # if hasattr(emission.args[0], 'statement'):
                    item = emission.args[0]
                    self.proof_step.statement = item.statement
                    # FIXME Obsolete: Set target selected if no selection
                    if not self.current_selection and not self.target_selected:
                        self.emw.process_target_click()
                    self.__server_call_statement(item)

                elif emission.is_from(self.statement_dropped):
                    # Statement dropped into context
                    item = emission.args[0]
                    # print(f"Statement dropped: {item.statement.lean_name}")
                    self.proof_step.statement = item.statement

                    # Empty selection and call statement
                    self.emw.empty_current_selection()
                    self.emw.target_selected = False
                    self.__server_call_statement(item)

                elif emission.is_from(self.math_object_dropped):
                    # Determine an Action Button from selection and receiver
                    # and call __server_call_action

                    log.debug("Math object dropped!")
                    # s = [item.math_object.to_display(format_="utf8")
                    #      for item in self.emw.current_selection]
                    # log.debug(f"Selection: {s}")
                    premise_item = emission.args[0]  # MathWidgetItem
                    op_item = emission.args[1]  # Optional[MathWidgetItem]
                    await self.__server_call_d_n_n(premise_item, op_item)
                    # Operator is None if dropping did not occur on a property.
                    # Then WrongUI exception will be raised by drag_n_drop().

                    # # selection = self.current_selection_as_mathobjects
                    # operator = op_item.math_object if op_item else None
                    # premise = premise_item.math_object if premise_item else None
                    # #     selection.remove(operator)
                    #
                    # self.proof_step.drag_n_drop = DragNDrop(premise, operator)
                    # try:
                    #     names = drag_n_drop(premise, operator,
                    #                         self.action_button_names)
                    # except WrongUserInput as error:
                    #     self.proof_step.user_input = self.emw.user_input
                    #     self.process_wrong_user_input(error)
                    #
                    # else:
                    #     # Only first name is tried
                    #     for name in names:
                    #         action_btn = ActionButton.from_name.get(name)
                    #         if action_btn:
                    #             self.proof_step.button_name = name
                    #             # Fixme: ne marche pas
                    #             selection = self.current_selection_as_mathobjects
                    #             self.proof_step.selection = selection
                    #             self.proof_step.target_selected = self.emw.target_selected
                    #             await self.emw.simulate(self.proof_step,
                    #                                     duration=0.5)
                    #             # await action_btn.simulate(duration=0.5)
                    #             # self.__server_call_action(action_btn)
                    #             break
                    #     # No button found: this should not happen

    ###################
    # History actions #
    ###################
    def history_undo(self):
        """
        Go one step backward in history in the lean_file.
        """
        self.lean_file.undo()
        self.process_history_move()

    def history_redo(self):
        """
        Go one step forward in history in the lean_file.
        """
        self.lean_file.redo()
        self.process_history_move()

    def history_rewind(self):
        """
        Go to beginning of history in the lean_file.
        """
        self.lean_file.rewind()
        self.process_history_move()

    def history_go_to_end(self):
        """
        Go to end of history in the lean_file.
        """
        self.lean_file.go_to_end()
        self.process_history_move()

    def history_goto(self, history_nb):
        """
        Move to a specific place in the history of the Lean file.
        """
        self.lean_file.goto(history_nb)
        self.process_history_move()

    def process_history_move(self):
        """
        This method is called after lean_file has been updated according to
        the history move.
        - update self.proof_tree.current_goal_node.
        - Update interface, and prepare next proof_step.
        """
        historic_proof_step = self.lean_file.current_proof_step
        children_goal_nodes = historic_proof_step.children_goal_nodes
        proof_state = historic_proof_step.proof_state
        self.proof_step.proof_state = proof_state
        self.proof_step.children_goal_nodes = children_goal_nodes

        # ─────── Update proof_tree ─────── #
        self.proof_tree.current_goal_node = children_goal_nodes[0]
        self.proof_tree.last_proof_step = historic_proof_step

        # ─────── Update proof_step ─────── #
        # From here, self.proof_step is replaced by a new proof_step!
        self.previous_proof_step = self.proof_step
        self.update_proof_step()

        # ─────── Update UI ─────── #
        log.info("** Updating UI **")
        self.unfreeze()
        if self.proof_step.is_error():  # Should not happen?!
            self.emw.update_goal(None)
        else:
            self.emw.update_goal(proof_state.goals[0])

    ################################################
    # Actions that send code to Lean (via servint) #
    ################################################

    async def __server_call_d_n_n(self, premise_item, op_item):
        # selection = self.current_selection_as_mathobjects
        operator = op_item.math_object if op_item else None
        premise = premise_item.math_object if premise_item else None
        #     selection.remove(operator)

        self.proof_step.drag_n_drop = DragNDrop(premise, operator)
        try:
            names = drag_n_drop(premise, operator,
                                self.action_button_names)
        except WrongUserInput as error:
            self.proof_step.user_input = self.emw.user_input
            self.process_wrong_user_input(error)
            return

        # Only first name is tried
        for name in names:
            action_btn = ActionButton.from_name.get(name)
            if action_btn:
                self.proof_step.button_name = name
                selection = self.current_selection_as_mathobjects
                self.proof_step.selection = selection
                self.proof_step.target_selected = self.emw.target_selected
                user_action = self.proof_step.user_action
                # log.info("Simulating proof_step with:")
                # print(user_action)
                await self.emw.simulate_user_action(user_action,
                                                    duration=0.5,
                                                    execute_action=True)

                # await action_btn.simulate(duration=0.5)
                # self.__server_call_action(action_btn)
                break
        # No button found: this should not happen

    def __server_call_action(self, action_btn):
        """
        Call the action corresponding to action_btn.

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

        action = action_btn.action
        log.debug(f'------ Calling action {action.symbol} ------')
        # Send action and catch exception when user needs to:
        #   - choose A or B when having to prove (A OR B) ;
        #   - enter an element when clicking on 'exists' button.
        #   - and so on.
        selection = self.current_selection_as_mathobjects
        self.proof_step.selection = selection
        self.proof_step.target_selected = self.emw.target_selected

        while True:
            try:
                self.proof_step.user_input = self.emw.user_input
                lean_code = action.run(self.proof_step)

            except MissingParametersError as e:
                if e.input_type == InputType.Text:
                    # TODO: move this into EMW methods
                    choice, ok = QInputDialog.getText(action_btn,
                                                      e.title,
                                                      e.output)
                elif e.input_type in (InputType.Choice, InputType.YesNo):
                    choice, ok = ButtonsDialog.get_item(e.choices,
                                                        e.title,
                                                        e.output)
                if ok:
                    self.emw.user_input.append(choice)
                else:
                    self.emw.user_input = []
                    self.unfreeze()
                    break

            except WrongUserInput as error:
                self.proof_step.user_input = self.emw.user_input
                self.process_wrong_user_input(error)
                break

            else:
                self.proof_step.lean_code = lean_code
                self.proof_step.user_input = self.emw.user_input

                # Update lean_file and call Lean server
                self.lean_code_sent = lean_code
                # previous_proof_state = self.proof_step.proof_state
                task = Task(fct=self.servint.code_insert,
                            kwargs={'proof_step': self.proof_step,
                                    'label': action.symbol,
                                    'cancel_fct': self.lean_file.undo})
                self.send_task_to_server(task)
                break

    def __server_call_statement(self, item):
        """
        This function is called when the user clicks on a Statement he wants to
        apply. The statement can be either a Definition or a Theorem. the code
        is then inserted to the server.
        """

        selection = self.current_selection_as_mathobjects
        self.proof_step.selection = selection
        self.proof_step.target_selected = self.emw.target_selected

        try:
            item.setSelected(False)
            statement = item.statement

            if isinstance(statement, Definition):
                lean_code = generic.action_definition(self.proof_step)

            elif isinstance(statement, Theorem):
                lean_code = generic.action_theorem(self.proof_step)
        except WrongUserInput as error:
            self.process_wrong_user_input(error)

        else:
            log.debug(f'Calling statement {item.statement.pretty_name}')
            self.proof_step.lean_code = lean_code

            # Update lean_file and call Lean server
            self.lean_code_sent = lean_code
            task = Task(fct=self.servint.code_insert,
                        kwargs={'proof_step': self.proof_step,
                                'label': statement.pretty_name,
                                'cancel_fct': self.lean_file.undo})
            self.send_task_to_server(task)

    def __server_send_editor_lean(self):
        """
        Send the L∃∀N code written in the L∃∀N editor widget to the
        server interface.
        """
        task = Task(fct=self.servint.code_set,
                    kwargs={'proof_step': self.proof_step,
                            'label': "code_set",
                            'cancel_fct': self.lean_file.undo,
                            'code': self.lean_editor.code_get()})
        self.send_task_to_server(task)

    #########################
    #########################
    # Process Lean response #
    #########################
    #########################

    def process_wrong_user_input(self, error):
        """
        This is the special method called when a WrongUserInput exception
        occurs. In this case, no new code is sent to the Lean server,
        and thus self.process_lean_response is NOT called.
        """
        self.proof_step.error_type = 1
        self.proof_step.error_msg = error.message

        self.update_proof_step()

        self.emw.process_wrong_user_input()
        self.unfreeze()
        self.emw.update_goal(None)
        self.emw.ui_updated.emit()

    @staticmethod
    def automatic_actions(goal: Goal) -> UserAction:
        """
        Return a UserAction if some automatic_intro is on and there is a
        pertinent automatic action to perform. Automatic actions include:
        (1) Intro of a variable when some context property if an
        existential statement.
        (2) Intro of premise when an implication appears in the context.
        This happens only if premise is not obviously in the context.
        The user is asked if OK.
        (3) Intro of variables and hypotheses when target is a
        universal statement or an implication.
        """

        target = goal.target

        user_action = None
        # (1) Check automatic intro of existence hypos
        auto_exists = cvars.get("functionality.automatic_intro_of_exists", True)
        if auto_exists:
            prop: ContextMathObject
            for prop in goal.context_props:
                if prop.is_exists() and prop.allow_auto_action:
                    user_action = UserAction(selection=[prop],
                                             button_name="exists_use")
                    # Turn off auto_action for this prop:
                    prop.turn_off_auto_action()
                    return user_action

        # (2) Check automatic intro of hypos' premises
        ask_auto_premises = cvars.get(
            "functionality.ask_to_prove_premises_of_implications", True)
        context_types = [p.math_type for p in goal.context_props]
        for prop in goal.context_props:
            premise = prop.premise()  # None if prop is not an implication
            if premise and prop.allow_auto_action:
                # (1) If premise is in context, do nothing unless
                # it is an inequality,
                # in which case add auto action without asking usr
                if premise == target.math_type:
                    continue
                elif premise in context_types:
                    if not premise.is_inequality(is_math_type=True):
                        continue
                    # Premise is an inequality in the context: do apply!
                    prop.turn_off_auto_action()
                    index = context_types.index(premise)
                    context_premise = goal.context_props[index]
                    user_action = UserAction(selection=[context_premise, prop],
                                             button_name="implies_use")
                    return user_action
                elif ask_auto_premises:
                    prop.turn_off_auto_action()  # No more asking for this one
                    msg_box = QMessageBox()
                    msg_box.setText(_('Do you want to prove the premise "{}" '
                                      'as a new sub-goal?')
                                    .format(premise.to_display(format_='utf8')))
                    msg_box.addButton(_('Yes'), QMessageBox.YesRole)
                    no_button = msg_box.addButton(_('No'), QMessageBox.NoRole)
                    msg_box.exec_()
                    if msg_box.clickedButton() != no_button:
                        user_action = UserAction(selection=[prop],
                                                 user_input=[0],
                                                 button_name="implies_use")
                    return user_action

        # (3) Check automatic intro of variables and hypotheses
        auto_for_all = cvars.get("functionality.automatic_intro_of" +
                                 "_variables_and_hypotheses", False)
        if auto_for_all and target.allow_auto_action:
            if target.is_for_all():
                user_action = UserAction.simple_action("forall_prove")
                target.turn_off_auto_action()
                return user_action
            elif target.is_implication():
                user_action = UserAction.simple_action("implies_prove")
                target.turn_off_auto_action()
                return user_action

    def process_automatic_actions(self, goal):
        """
        Perform the UserAction returned by self.automatic_action, if any.
        emw.automatic_action is set to True so that emw knows about it,
        in particular TargetSelected will be true whatever.
        """
        user_action = Coordinator.automatic_actions(goal)
        if user_action:
            self.emw.automatic_action = True
            # log.debug(f"Automatic action: {action}")
            self.proof_step.is_automatic = True
            # Async call to emw.simulate_user_action:
            self.freeze()
            self.nursery.start_soon(self.emw.simulate_user_action, user_action)

    def freeze(self):
        self.is_frozen = True
        self.emw.freeze(True)
        self.frozen.emit()

    def unfreeze(self):
        """
        Unfreeze the UI. Deal with special cases: no_more_goal,
        history_at_beginning, history_at_end.
        """
        # TODO: put this in EMW

        if self.lean_file.current_proof_step \
                and not self.lean_file.current_proof_step.no_more_goal:
            self.emw.freeze(False)
        else:  # If no more goals, disable actions but enable toolbar
            self.emw.ecw.freeze(True)
            self.toolbar.setEnabled(True)
        at_beginning = self.servint.lean_file.history_at_beginning
        at_end = self.servint.lean_file.history_at_end

        self.emw.history_button_unfreeze(at_beginning, at_end)
        self.is_frozen = False
        self.unfrozen.emit()

    # @Slot(CodeForLean)
    # def process_effective_code(self, effective_lean_code: CodeForLean):
    #     """
    #     Replace the (maybe complicated) Lean code in the Lean file by the
    #     portion of the code that was effective.
    #
    #     This is called by a signal in servint.
    #     """
    #     code = effective_lean_code.to_code()
    #     log.debug(f"Replacing code by effective code {code}")
    #     self.proof_step.effective_code = effective_lean_code
    #     self.servint.history_replace(effective_lean_code)

    def process_failed_request_error(self, errors):
        lean_code = self.proof_step.lean_code
        if lean_code and lean_code.error_msg:
            self.proof_step.error_msg = lean_code.error_msg
        else:
            self.proof_step.error_msg = _('Error')

        details = ""
        for error in errors:
            details += "\n" + error.text
        log.debug(f"Lean errors, details: {details}")

    def process_error(self, error_type, errors):
        """
        Note that history_delete will be called, and then process_lean_response
        again.
        """
        self.proof_step.error_type = error_type
        if error_type == 1:  # FailedRequestError
            self.process_failed_request_error(errors)
        elif error_type == 3:  # Timeout
            self.proof_step.error_msg = _("I've got a headache, try again...")
            log.debug("Lean timeout")
        elif error_type == 4:  # UnicodeDecodeError
            self.proof_step.error_msg = _("Unicode error, try again...")
            log.debug("Unicode Error")
        # elif error_type == 3:  # Timeout
        #     self.proof_step.error_msg = _("Error, no proof state, "
        #                                   "try again...")
        #     log.debug("Proof state is None!")
        elif error_type == 5:
            self.proof_step.error_msg = _("Unable to get new proof_state")

        elif error_type == 6:
            self.proof_step.error_msg = _("(File unchanged)")
        elif error_type == 7:
            self.proof_step.error_msg = _("Action cancelled")
        else:
            self.proof_step.error_msg = _("Undocumented error")

    def abort_process(self):
        log.debug("Aborting process")
        if not self.servint.lean_file.history_at_beginning:
            # Abort and go back to last goal
            self.lean_file.delete()
            self.unfreeze()
            self.update_proof_step()
            self.emw.update_goal(None)

        else:
            # Resent the whole code
            self.__initialize_exercise()

    def set_fireworks(self):
        """
        Replace the target by a message "No more goal", and return the
        resulting ProofState
        """

        self.proof_step.no_more_goal = True
        self.proof_step.success_msg = _("Proof complete")
        self.proof_step.new_goals = []
        # Artificially create a final proof_state by replacing target by a msg
        # (We do not get the final proof_state from Lean).
        proof_state = deepcopy(self.proof_step.proof_state)
        target = proof_state.goals[0].target
        target.math_type = MathObject.NO_MORE_GOALS

        return proof_state

    def display_fireworks_msg(self):
        """
        Display a QMessageBox informing that the proof is complete.
        """
        if not self.proof_step.is_redo() \
                and not self.proof_step.is_goto()\
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

    def update_proof_step(self):
        """
        Store proof_step and create next proof_step.
        This is called for every user action, including errors and history
        moves.
        """

        # Store journal and auto_step
        if not self.test_mode:
            self.journal.store(self.proof_step, self)
            # Fixme: compute only at end
            self.proof_step.auto_step = AutoStep.from_proof_step(
                                                            self.proof_step,
                                                            emw=self.emw)

        # Create next proof_step, and connect to ProofTree
        self.emw.displayed_proof_step = copy(self.proof_step)  # FIXME
        self.proof_step = ProofStep.next_(self.lean_file.current_proof_step,
                                          self.lean_file.target_idx)
        self.proof_step.parent_goal_node = self.proof_tree.current_goal_node

        # # Target in context?
        # solving_objs = context_obj_solving_target(self.proof_step)
        # self.proof_step.solving_objs = solving_objs
        self.proof_step_updated.emit()  # Received in auto_test

    def check_response_coherence(self, lean_response):
        """
        Check if lean_response concerns current proof step.
        """
        if not lean_response.proof_step:
            log.debug("No proof_step?!")
        elif lean_response.proof_step is not self.proof_step:
            gn1 = lean_response.proof_step.parent_goal_node
            gn2 = self.proof_step.parent_goal_node
            nb1 = gn1.goal_nb if gn1 else "?"
            nb2 = gn2.goal_nb if gn2 else "?"
            log.debug(f"Received proof step goal node #{nb1}, expecting #{nb2}")

        test = (not lean_response.proof_step or
                lean_response.proof_step is self.proof_step)
        return test

    def invalidate_events(self):
        # self.current_user_action = None
        self.lean_code_sent = None

    def save_history(self):
        key = 'functionality.save_history_of_solved_exercises'
        save_history = cvars.get(key, False)
        if save_history and (not self.test_mode and not self.history_mode):
            log.info("Saving history")

            # Compute AutoSteps string
            proof_steps = self.proof_tree.proof_steps()
            auto_steps = [AutoStep.from_proof_step(step, self.emw)
                          for step in proof_steps]
            auto_steps_str = ''
            for step in auto_steps:
                auto_steps_str += '    ' + step.raw_string + ',\n'
            additional_metadata = {'AutoTest': auto_steps_str}
            log.debug(additional_metadata)
            lean_code = self.lean_file.inner_contents

            self.exercise.save_with_auto_steps(
                additional_metadata=additional_metadata,
                lean_code=lean_code)

    @Slot()
    def process_lean_response(self, lean_response):
        """
        This method processes Lean response after a request, and is a slot
        of a signal emitted by self.servint when all info have been received.
        There are exactly three mutually exclusive possibilities:
        (1) Proof is complete,
        (2) The request has failed,
        (3) The request has succeeded but proof is not complete.

        Every action of the user (ie click on an ActionButton, a statement
        item, or a history move) which do not rise a WrongUserInput
        exception is passed to Lean, and then goes through this method.
        """

        log.debug("Lean response received")

        # (1) Test Response corresponds to request
        if not self.check_response_coherence(lean_response):
            log.warning("Lean response with incoherent proof step, ignoring")
            # self.abort_process()
            return

        no_more_goals = lean_response.no_more_goals
        error_type = lean_response.error_type
        proof_state = lean_response.new_proof_state

        log.info("** Processing Lean's response **")
        history_nb = self.lean_file.target_idx
        log.info(f"History nb: {history_nb}")
        self.emw.automatic_action = False  # FIXME: move

        # ─────── Errors ─────── #
        if error_type != 0:
            log.info("  -> error!")
            self.process_error(error_type, lean_response.error_list)
            self.abort_process()
            return

        # if exercise != self.exercise:  # Should never happen
        #     log.warning("    not from current exercise, ignoring")
        #     return

        # ─────── First step ─────── #
        if not self.server_task_started.is_set():
            # log.debug("First proof step")
            self.start_server_task()

        # ─────── Compute proof state ─────── #
        if no_more_goals:
            log.info("  -> proof completed!")
            proof_state = self.set_fireworks()

        else:  # Generic step
            # hypo_analysis, targets_analysis = analysis
            # if hypo_analysis and targets_analysis:
            #     log.info("** Creating new proof state **")
            #     proof_state = ProofState.from_lean_data(hypo_analysis,
            #                                             targets_analysis,
            #                                             to_prove=True)
            if proof_state:
                self.lean_file.state_info_attach(ProofState=proof_state)
            else:
                # No proof state!? Maybe empty analysis?
                self.process_error(error_type=5, errors=[])
                log.debug(f"Analysis: {lean_response.analysis[0]} ///"
                          f" {lean_response.analysis[1]}")
                self.abort_process()
                return

        self.proof_step.proof_state = proof_state  # FIXME

        if not self.proof_step.is_error():
            if not self.proof_step.is_history_move():
                log.debug("     Storing proof step in lean_file info")
                self.lean_file.state_info_attach(proof_step=self.proof_step)
                self.proof_tree.process_new_proof_step(self.proof_step)
                # self.proof_step.unsolved_goal_nodes_after = \
                #     copy(self.proof_tree.unsolved_goal_nodes)
                # ugn = [gn.goal_nb for gn in self.proof_tree.unsolved_goal_nodes]
                # log.debug(f"Ps_unsolved_gn_after: {ugn}")

            # ─────── Check for new goals ─────── #
            # FIXME: obsolete. This is still used for the outline window though.
            delta = self.lean_file.delta_goals_count
            self.proof_step.delta_goals_count = delta
            self.proof_step.update_goals()

            # log.debug(f"    Target_idx: {self.lean_file.target_idx}")

        # ─────── Tag and sort new goal ─────── #
        if self.logically_previous_proof_step:
            new_goal: Goal = self.proof_step.goal
            used_properties = self.proof_step.used_properties()
            new_goal.mark_used_properties(used_properties)

        # ─────── Name all bound vars ─────── #
        log.info("** Naming dummy vars **")
        self.proof_step.goal.smart_name_bound_vars()

        # ─────── Update proof_step ─────── #
        # From here, self.proof_step is replaced by a new proof_step!
        self.previous_proof_step = self.proof_step
        self.update_proof_step()

        # ─────── Update UI ─────── #
        log.info("** Updating UI **")
        self.unfreeze()
        if self.proof_step.is_error():
            self.emw.update_goal(None)
        else:
            self.emw.update_goal(proof_state.goals[0])

        # ─────── Automatic actions ─────── #
        if not (self.previous_proof_step.is_history_move()
                or self.previous_proof_step.is_error()
                or self.test_mode):
            self.process_automatic_actions(proof_state.goals[0])

        self.emw.ui_updated.emit()  # For testing

        # FIXME: unused??
        self.invalidate_events()

        if no_more_goals:
            # Display QMessageBox but give deaduction time to properly update
            # ui before.
            QTimer.singleShot(0, self.display_fireworks_msg)
            self.save_history()

