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
from pathlib import Path
import trio
from typing import              Callable
import qtrio

from PySide2.QtCore import (    Signal,
                                Slot,
                                QEvent,
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

from deaduction.config import          (_,
                                        user_config,
                                        EXERCISE)
from deaduction.dui.utils import  (     replace_delete_widget,
                                        ButtonsDialog)
from deaduction.dui.widgets import (    ActionButton,
                                        ActionButtonsWidget,
                                        LeanEditor,
                                        StatementsTreeWidget,
                                        StatementsTreeWidgetItem,
                                        MathObjectWidget,
                                        MathObjectWidgetItem,
                                        TargetWidget)
from deaduction.pylib.actions import (  Action,
                                        action_apply,
                                        InputType,
                                        MissingParametersError,
                                        WrongUserInput)
import deaduction.pylib.actions.generic as generic
from deaduction.pylib.coursedata import (   Definition,
                                            Exercise,
                                            Theorem)
from deaduction.pylib.server.exceptions import FailedRequestError
from deaduction.pylib.mathobj import (  MathObject,
                                        Goal,
                                        ProofState,
                                        Proof)
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

# 
class ExerciseCentralWidget(QWidget):
    """
    Main / central / biggest widget in the exercise window. Self is to
    be instanciated as the central widget of d∃∀duction, more
    specifically as ExerciseMainWindow.centralWidget(). This widgets
    contains many crucial children widgets:
        - the target widget (self.target_wgt);
        - the 'context area' widgets:
            - the objects widget (self.objects_wgt) for math. objects
              (e.g. f:X->Y a function);
            - the properties widget (self.props_wgt) for math.
              properties (e.g. f is continuous);
        - the 'action area' widgets:
            - the logic buttons (self.logic_btns);
            - the proof buttons (self.proof_btns);
            - the magic buttons (self.magic_btns), if any
            - the statements tree (self.statements_tree, see
              StatementsTreeWidget.__doc__).

    All of these are instantiated in self.__init__ as widget classes
    defined elsewhere (mainly actions_widgets_classes.py and
    context_widgets_classes.py) and properly arranged in layouts.

    Self is instantiated with only an instance of the class Exercise.
    However, when this happens, it does not have a context nor a target
    (L∃∀N has not yet been called, see ExerciseMainWindow.__init__!):
    empty widgets are displayed for context elements. Once L∃∀N has been
    successfully called and sent back a goal (an instance of the class
    Goal contains a target, objects and properties, see
    deaduction.pylib.mathobj.Goal), context elements widgets are changed
    with the method update_goal. Note that neither the exercise (used in
    self.__init__) nor the goal are kept as class attributes!

    :attribute logic_btns ActionButtonsWidget: Logic buttons available
        for this exercise.
    :attribute objects_wgt MathObjectWidget: Widget for context
        objects (e.g. f:X->Y a function).
    :attribute proof_btns ActionButtonsWidget: Proof buttons
        available for this exercise.
    :attribute props_wgt MathObjectWidget: Widget for context
        properties (e.g. f is continuous).
    :attribute statements_tree StatementsTreeWidget: Tree widget for
        statements (theorems, definitions, past exercises) available to
        this exercise.
    :attribute target_wgt TargetWidget: Widget to display the context
        target.

    :property actions_buttons [ActionButtons]: A list of all objects
        and properties (instances of the class MathObjectWidgetItem).
    :property context_items [MathObjectWidgetItems]: A list of all
        objects and properties (instances of the class
        MathObjectWidgetItem).
    """

    def __init__(self, exercise: Exercise):
        """
        Init self with an instance of the class Exercise. See
        self.__doc__.

        :param exercise: The instance of the Exercise class representing
            the exercise to be solved by the user.
        """

        super().__init__()

        # ───────────── Init layouts and boxes ───────────── #
        # I wish none of these were class atributes, but we need at
        # least self.__main_lyt and self.__context_lyt in the method
        # self.update_goal.

        self.__main_lyt     = QVBoxLayout()
        self.__context_lyt  = QVBoxLayout()
        context_actions_lyt = QHBoxLayout()
        actions_lyt         = QVBoxLayout()
        action_btns_lyt     = QVBoxLayout()

        action_btns_lyt.setContentsMargins(0, 0, 0, 0)
        action_btns_lyt.setSpacing(0)

        actions_gb = QGroupBox(_('Actions (transform context and target)'))
        context_gb = QGroupBox(_('Context (objects and properties)'))

        # ──────────────── Init Actions area ─────────────── #

        self.logic_btns = ActionButtonsWidget(exercise.available_logic)
        self.proof_btns = ActionButtonsWidget(exercise.available_proof)
        self.magic_btns = ActionButtonsWidget(exercise.available_magic)

        # Search for ActionButton corresponding to action_apply
        # (which will be called by double-click):
        apply_buttons = [button for button in self.proof_btns.buttons
                         if button.action.run == action_apply]

        if apply_buttons:
            self.action_apply_button = apply_buttons[0]
        else:
            log.warning("Action_apply_button not found")

        statements           = exercise.available_statements
        outline              = exercise.course.outline
        self.statements_tree = StatementsTreeWidget(statements, outline)

        # ─────── Init goal (Context area and target) ────── #

        self.objects_wgt = MathObjectWidget()
        self.props_wgt   = MathObjectWidget()
        self.target_wgt  = TargetWidget()

        # ───────────── Put widgets in layouts ───────────── #

        # Actions
        action_btns_lyt.addWidget(self.logic_btns)
        action_btns_lyt.addWidget(self.proof_btns)
        if exercise.available_magic:
            action_btns_lyt.addWidget(self.magic_btns)
        actions_lyt.addLayout(action_btns_lyt)
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

    ##############
    # Properties #
    ##############

    @property
    def actions_buttons(self) -> [ActionButton]:
        """
        Do not delete! A list of all logic buttons and proof
        buttons (instances of the class ActionButton).
        """

        return self.logic_btns.buttons \
                + self.proof_btns.buttons \
                + self.magic_btns.buttons

    ###########
    # Methods #
    ###########

    def freeze(self, yes=True):
        """
        Freeze interface (inactive widgets, gray appearance, etc) if
        yes:
            - disable objects and properties;
            - disable all buttons;
        unfreeze it otherwise.

        :param yes: See above.
        """

        to_freeze = [self.objects_wgt,
                     self.props_wgt,
                     self.logic_btns,
                     self.proof_btns,
                     self.magic_btns,
                     self.statements_tree]
        for widget in to_freeze:
            widget.setEnabled(not yes)

    def update_goal(self, new_goal: Goal, goal_count: str = ''):
        """
        Change goal widgets (self.objects_wgts, self.props_wgt and
        self.target_wgt) to new widgets, corresponding to new_goal.

        :param new_goal: The goal to update self to.
        :param goal_count: a string indicating the goal_count state,
        e.g. "  2 / 3" means the goal number 2 out of 3 is currently being
        studied
        """

        # Init context (objects and properties). Get them as two list of
        # (MathObject, str), the str being the tag of the prop. or obj.
        new_context    = new_goal.tag_and_split_propositions_objects()
        new_target     = new_goal.target
        new_target_tag = '='  # new_target.future_tags[1]
        new_objects    = new_context[0]
        new_props      = new_context[1]

        new_objects_wgt = MathObjectWidget(new_objects)
        new_props_wgt   = MathObjectWidget(new_props)
        new_target_wgt  = TargetWidget(new_target, new_target_tag, goal_count)

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
           (self.current_context_selection);
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
    :attribute current_context_selection [MathObjectWidgetItem]: The ordered
        of currently selected math. objects and properties by the user.
    :attribute ecw ExerciseCentralWidget: The instance of
        ExerciseCentralWidget instantiated in self.__init__, see
        ExerciseCentraiWidget.__doc__.
    :attribute lean_editor LeanEditor: A text editor to live-edit lean
        code.
    :attribute servint ServerInterface: The instance of ServerInterface
        for the session, instantiated in deaduction.dui.__main__.py.
    :attribute toolbar QToolBar: The toolbar.
    """

    window_closed                   = Signal()
    __action_triggered              = Signal(ActionButton)
    __apply_math_object_triggered   = Signal(MathObjectWidget)
    __statement_triggered           = Signal(StatementsTreeWidgetItem)

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

        # ─────────────────── Attributes ─────────────────── #

        self.exercise           = exercise
        self.current_goal       = None
        self.current_context_selection  = []
        self.ecw                = ExerciseCentralWidget(exercise)
        self.lean_editor        = LeanEditor()
        self.servint            = servint
        self.toolbar            = ExerciseToolbar()

        # ─────────────────────── UI ─────────────────────── #

        self.setCentralWidget(self.ecw)
        self.addToolBar(self.toolbar)
        self.toolbar.redo_action.setEnabled(False)  # No history at beginning
        self.toolbar.undo_action.setEnabled(False)  # same

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
        self.servint.nursery.start_soon(self.server_task)  # Start server task

    ###########
    # Methods #
    ###########

    def closeEvent(self, event: QEvent):
        """
        Overload native Qt closeEvent method — which is called when self
        is closed — to send the signal self.window_closed.

        :param event: Some Qt mandatory thing.
        """

        super().closeEvent(event)
        self.window_closed.emit()

    @property
    def current_context_selection_as_mathobjects(self):
        """
        Do not delete, used many times! Return the current selection as
        an ordered list of instances of the class MathObject directly.

        :return: See above.
        """

        return [item.mathobject for item in self.current_context_selection]

    def pretty_current_selection(self) -> str:
        """
        Return the current selection as a string, for display.

        :return: See above.
        """

        msg = 'Current user selection: '
        msg += str([item.text() for item in self.current_context_selection])

        return msg

    def update_goal(self, new_goal: Goal):
        """
        Change widgets (target, math. objects and properties) to
        new_goal and update internal mechanics accordingly.

        :param new_goal: The new goal to update / set the interface to.
        """

        # Init context (objects and properties). Get them as two list of
        # (MathObject, str), the str being the tag of the prop. or obj.

        # get old goal and set tags
        # TODO: make a separate method get_old_goal(lean_file)
        lean_file = self.servint.lean_file

        if lean_file.idx > 0:
            # NB : when idx = 0, old_goal = new_goal : nothing is new
            previous_idx = lean_file.idx - 1
            entry = lean_file.history[previous_idx]
            entry_info = entry.misc_info
            log.debug(f'Proof step n°{lean_file.idx}')

            if 'ProofState' in entry_info.keys():
                previous_proof_state = entry_info['ProofState']
                old_goal = previous_proof_state.goals[0]
                Goal.compare(new_goal, old_goal, goal_is_new=False)  # set tags
            else:
                log.warning(f"No proof state found for previous step")

        # FIXME: target tag
        # new_target_tag = '='
        # try:
        #     new_target_tag = new_goal.future_tags[1]
        # except AttributeError:
        #     log.debug('no tag for target')
        #     pass

        # new_context = new_goal.tag_and_split_propositions_objects()

        # Count of goals
        total_goals_counter, \
            current_goal_number, \
            current_goals_counter, \
            goals_counter_evolution \
            = self.count_goals()
        goal_count = f'  {current_goal_number} / {total_goals_counter}'
        # log.debug(f"Goal  {goal_count}")

        # Display if a goal has been solved and user is not undoing
        if goals_counter_evolution < 0 and current_goals_counter != 0:
            if EXERCISE.last_action != 'undo':
                log.info(f"Current goal solved!")
                QMessageBox.information(self,
                                        '',
                                        _('Current goal solved'),
                                        QMessageBox.Ok
                                        )
        EXERCISE.last_action = None

        # Reset current context selection
        self.clear_current_selection()

        # Update UI and attributes
        self.ecw.update_goal(new_goal, goal_count)
        self.current_goal = new_goal

        # Reconnect Context area signals and slots
        self.ecw.objects_wgt.itemClicked.connect(self.process_context_click)
        self.ecw.props_wgt.itemClicked.connect(self.process_context_click)
        if hasattr(self.ecw, "action_apply_button"):
            self.ecw.objects_wgt.apply_math_object_triggered.connect(
                self.__apply_math_object_triggered)
            self.ecw.props_wgt.apply_math_object_triggered.connect(
                self.__apply_math_object_triggered)

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
        """

        self.freeze()
        await self.servint.exercise_set(self.exercise)
        self.freeze(False)

        async with qtrio.enter_emissions_channel(
                signals=[self.lean_editor.editor_send_lean,
                         self.toolbar.redo_action.triggered,
                         self.window_closed,
                         self.toolbar.undo_action.triggered,
                         self.__action_triggered,
                         self.__statement_triggered,
                         self.__apply_math_object_triggered]) as emissions:
            async for emission in emissions.channel:
                if emission.is_from(self.lean_editor.editor_send_lean):
                    await self.process_async_signal(self.__server_send_editor_lean)

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
                    await self.process_async_signal(partial(
                            self.__server_call_action, emission.args[0]))

                elif emission.is_from(self.__statement_triggered):
                    await self.process_async_signal(partial(
                            self.__server_call_statement, emission.args[0]))

                elif emission.is_from(self.__apply_math_object_triggered):
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
        except FailedRequestError as e:
            # Display an error message
            # TODO: make it a separate class
            message_box = QMessageBox(self)
            message_box.setIcon(QMessageBox.Critical)
            message_box.setWindowTitle(_('Action not understood'))
            message_box.setText(_('Action not understood'))

            detailed = ""
            for error in e.errors:
                rel_line_number = error.pos_line \
                                  - self.exercise.lean_begin_line_number
                detailed += f'* at {rel_line_number}: {error.text}\n'

            message_box.setDetailedText(detailed)
            message_box.setStandardButtons(QMessageBox.Ok)
            message_box.exec_()

            # Abort and go back to last goal
            await self.servint.history_undo()

        finally:
            self.freeze(False)
            # Required because history is always changed with signals
            self.toolbar.undo_action.setEnabled(
                    not self.servint.lean_file.history_at_beginning)
            self.toolbar.redo_action.setEnabled(
                    not self.servint.lean_file.history_at_end)

    # ─────────────── Specific functions ─────────────── #
    # To be called as process_function in the above

    async def __server_call_action(self, action_btn: ActionButton):
        # TODO: docstring me

        action     = action_btn.action
        user_input = []
        log.debug(f'Calling action {action.symbol}')
        # Send action and catch exception when user needs to:
        #   - choose A or B when having to prove (A OR B) ;
        #   - enter an element when clicking on 'exists' button.

        while True:
            try:
                if user_input == []:
                    code = action.run(self.current_goal,
                            self.current_context_selection_as_mathobjects)
                else:
                    code = action.run(self.current_goal,
                            self.current_context_selection_as_mathobjects,
                            user_input)
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
            except WrongUserInput as e:
                self.clear_current_selection()
                await self.display_WrongUserInput(e)
                break
            else:
                log.info("Code sent to lean: " + code)
                await self.servint.code_insert(action.symbol, code)
                break

    async def __server_call_apply(self, item: MathObjectWidgetItem):
        """
        This function is called when user double-click on an item in the
        context area The item is added to the end of the
        current_context_selection, and the action corresponding to the "apply"
        button is called
        """

        item.mark_user_selected(True)

        if item in self.current_context_selection:
            self.current_context_selection.remove(item)
        self.current_context_selection.append(item)

        await self.process_async_signal(partial(self.__server_call_action,
                                                self.ecw.action_apply_button))

    async def __server_call_statement(self, item: StatementsTreeWidgetItem):
        # TODO: docstring me

        # Do nothing if user clicks on a node
        if isinstance(item, StatementsTreeWidgetItem):
            try: 
                item.setSelected(False)
                statement = item.statement

                if isinstance(statement, Definition):
                    code = generic.action_definition(self.current_goal,
                            self.current_context_selection_as_mathobjects,
                                                     statement)
                elif isinstance(statement, Theorem):
                    code = generic.action_theorem(self.current_goal,
                            self.current_context_selection_as_mathobjects,
                                                  statement)

                log.debug(f'Calling statement {item.statement.pretty_name}')
                log.debug("Code sent to Lean: " + code)
                await self.servint.code_insert(statement.pretty_name, code)
            except WrongUserInput as e:
                self.clear_current_selection()
                await self.display_WrongUserInput(e)

    async def __server_send_editor_lean(self):
        """
        Send the L∃∀N code written in the L∃∀N editor widget to the
        server interface.
        """

        await self.servint.code_set(_('Code from editor'),
                                    self.lean_editor.code_get())

    async def display_WrongUserInput(self, e):
        details = e.error
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(_('Action not understood'))
        msg_box.setText(_("don't know what to do with your input!"))
        display_errors = user_config['display_detailed_errors_on_WUI']
        if details and display_errors:
            msg_box.setDetailedText(details)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    #########
    # Slots #
    #########

    @Slot()
    def clear_current_selection(self):
        """
        Clear current (user) selection of math. objects and properties.
        """

        # No need to call mark_user_selected on current selection's items
        # because this is cosmetics and widgets are destroyed and re-created at
        # each goal change anyway.
        self.current_context_selection = []

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
        - replace the target by a message "Proof complete"
        """
        # TODO: make it a separate class
        QMessageBox.information(self,
                                _('Target solved'),
                                _('The proof is complete!'),
                                QMessageBox.Ok
                                )
        # make fake target to display message
        no_more_goal_text = "No more goal"
        target = self.current_goal.target
        target.math_type = MathObject(  node=no_more_goal_text,
                                        info={},
                                        children=[],
                                      )
        self.ecw.update_goal(self.current_goal, goal_count='')

    @Slot(MathObjectWidgetItem)
    def process_context_click(self, item: MathObjectWidgetItem):
        """
        Add or remove item (item represents a math. object or property)
        from the current selection, depending on whether it was already
        selected or note.

        :item: The math. object or property user just clicked on.
        """

        # One clicked, one does not want the item to remain visually
        # selected
        item.setSelected(False)

        if item not in self.current_context_selection:
            item.mark_user_selected(True)
            self.current_context_selection.append(item)
        else:
            item.mark_user_selected(False)
            self.current_context_selection.remove(item)

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
        which includes the new goal.

        :proofstate: The proofstate one wants to update self to.
        """

        # Weird that this methods only does this.
        # TODO: maybe delete it to only have self.update_goal?
        self.update_goal(proofstate.goals[0])

    ###################
    # Logical methods #
    ###################
    # The following methods are closer to the logical aspect of deaduction:
    # - the proof method essentially returns the sequence of successive
    # ProofState from the beginning of the proof until the current ProofState.
    # This sequence is obtained from the information attached to the lean_file
    # which provides a reliable account of the proof history.
    # This sequence is an instance of the Proof class, from proof_state.py
    # - the count_goals method then applies the count_goals_from_proof method
    # to the Proof instance, to get information on the proof history:
    # essentially
    #       - the total number of goals that have been examined during
    #       the proof history,
    #       - the number of the goal that the user is currently trying to prove

    def proof(self) -> Proof:
        """
        Return the current proof history, an instance of the Proof class
        """
        lean_file = self.servint.lean_file
        proof = Proof([(entry.misc_info["ProofState"], None) \
                 for entry in lean_file.history[:lean_file.target_idx+1]])
        return proof

    def count_goals(self) -> (int, int, int):
        """
        Compute and return three values:
            - total_goals_counter : total number of goals during Proof history
            - current_goal_number = number of the goal under study
            - current_goals_counter = number of goals at end of Proof
            - goals_counter_evolution = last evolution :
                > 0 means that new goal has appeared
                < 0 means that a goal has been solved
        """
        proof = self.proof()
        return proof.count_goals_from_proof()
