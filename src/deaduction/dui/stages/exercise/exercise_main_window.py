"""
##############################################################
# exercise_main_window.py : Provide ExerciseMainWindow class #
##############################################################

Author(s)      : Kryzar <antoine@hugounet.com>
Maintainers(s) : Kryzar <antoine@hugounet.com>
                 Frédéric Le Roux <frederic.le_roux@imj-prg.fr>
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

import                logging
from typing import    Union

from PySide2.QtCore    import (Signal,
                               Slot,
                               QEvent,
                               QSettings,
                               QModelIndex)
from PySide2.QtWidgets import (QMainWindow,
                               QMessageBox,
                               QAction)

import deaduction.pylib.config.vars      as     cvars
from deaduction.pylib.coursedata        import  Exercise, UserAction
from deaduction.pylib.mathobj           import (MathObject,
                                                ProofStep)

from deaduction.dui.elements            import (ActionButton,
                                                LeanEditor,
                                                StatementsTreeWidgetItem,
                                                StatementsTreeWidgetNode,
                                                MathObjectWidget,
                                                MathObjectWidgetItem,
                                                MenuBar,
                                                MenuBarAction,
                                                ConfigMainWindow,
                                                ProofOutlineWindow)
from ._exercise_main_window_widgets     import (ExerciseCentralWidget,
                                                ExerciseStatusBar,
                                                ExerciseToolBar)

log = logging.getLogger(__name__)
global _


class ExerciseMainWindow(QMainWindow):
    """
    This class is responsible for managing the whole interface for exercises.
    The communication with a so-called server interface, a middle man
    between the interface and L∃∀N, is done in the Coordinator class,
    which listen to ExerciseMainWindow's signals to handle user actions.

    User interface, server interface and L∃∀N server are different entities
    which remain separated by design; Qt signals and slots are used for
    communication between them. For the interface, self instantiates
    ExerciseCentralWidget, a toolbar, and probably more things in the future.
    For the communication with Coordinator.servint, self:
        1. stores user selection of math. objects or properties
           (self.current_selection);
        2. detects when an action button (in self.ecw.logic_btns or
           in self.ecw.proof_btns) or a statement (in
           self.ecw.statements_tree) is clicked on;

        Then the Coordinator class is responsible for handling the next steps:
        3. sends (the current goal, current selection) and ((clicked
           action button (with self.__server_call_action)) xor (clicked
           statement (with self.__server_call_statement))) to the server
           interface;
        4. waits for some response (e.g. a new goal, an exception asking
           for new user parameters).

    :attribute exercise Exercise: The instance of the Exercise class
        representing the exercise to be solved by the user, instantiated
        in deaduction.dui.__main__.py.
    :attribute lean_file VirtualFile: this object contains all the history
    of the proof, and in particular all proof_steps and corresponding Lean
    code content.
    :attribute current_goal Goal: The current goal, which contains the
        tagged target, tagged math. objects and tagged math. properties.
    :attribute current_selection [MathObjectWidgetItem]: The ordered of
        currently selected math. objects and properties by the user.
    :attribute ecw ExerciseCentralWidget: The instance of
        ExerciseCentralWidget instantiated in self.__init__, see
        ExerciseCentraiWidget.__doc__.
    :attribute lean_editor LeanEditor: A text editor to live-edit lean
        code.
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
    # Signals for WindowManager and testing:
    window_closed                = Signal()
    change_exercise              = Signal()
    ui_updated                   = Signal()
    # User action signals:
    action_triggered             = Signal(ActionButton)
    apply_math_object_triggered  = Signal(MathObjectWidget)
    statement_triggered          = Signal(StatementsTreeWidgetItem)

    def __init__(self, exercise: Exercise):
        """
        Init self with an instance of the exercise class. See self.__doc__.
        """

        super().__init__()
        self.setWindowTitle(f'{exercise.pretty_name} — d∃∀duction')

        # ─────────────────── Data ─────────────────── #
        # From outside
        self.exercise             = exercise
        self.lean_file            = None
        self.current_goal         = None
        self.displayed_proof_step = None
        self.test_mode            = False
        self.automatic_action     = False

        # From inside
        self.current_selection    = []
        self._target_selected     = False
        self.user_input           = []
        self.double_clicked_item  = None
        self.freezed              = False

        # ─────────────────────── Elements ─────────────────────── #

        self.ecw                  = ExerciseCentralWidget(exercise)
        self.lean_editor          = LeanEditor()
        self.toolbar              = ExerciseToolBar()
        self.proof_outline_window = ProofOutlineWindow()
        self.statusBar = ExerciseStatusBar(self)

        # ─────────────────────── UI ─────────────────────── #

        self.setCentralWidget(self.ecw)
        self.addToolBar(self.toolbar)
        self.toolbar.redo_action.setEnabled(False)  # No history at beginning
        self.toolbar.undo_action.setEnabled(False)  # same
        self.toolbar.rewind.setEnabled(False)  # same
        self.__init_menubar()
        self.setStatusBar(self.statusBar)

        settings = QSettings("deaduction")
        if settings.value("emw/Geometry"):
            self.restoreGeometry(settings.value("emw/Geometry"))

        self.close_coordinator = None  # Method set up by Coordinator

        self.__connect_signals()
        self.freeze()  # Wait for data before allowing user actions.

    #######################
    # Init /close methods #
    #######################

    def __connect_signals(self):
        """
        Connect all signals. Called at init.
        """
        # Actions area
        for action_button in self.ecw.actions_buttons:
            action_button.action_triggered.connect(self.action_triggered)
        self.ecw.statements_tree.itemClicked.connect(
                                            self.statement_triggered_filter)

        # UI
        self.toolbar.toggle_lean_editor_action.triggered.connect(
                self.lean_editor.toggle)
        self.toolbar.toggle_proof_outline_action.triggered.connect(
                self.proof_outline_window.toggle)
        self.toolbar.change_exercise_action.triggered.connect(
                                                    self.change_exercise)

    def __init_menubar(self):
        """
        Create ExerciseMainWindow's menubar. Relevant classes are MenuBar,
        MenuBarAction and MenuBarMenu, from deaduction.dui.elements.
        """
        # ─────────────────────── QActions ─────────────────────── #
        preferences = MenuBarAction(self, _("Preferences"))
        preferences.setMenuRole(QAction.PreferencesRole)
        preferences.triggered.connect(self.open_config_window)

        # ─────────────────────── Submenus ─────────────────────── #
        menu_deaduction = (_("Preferences"), [preferences])

        menu_exercise = (_('Exercise'),
                         [(_('Exercise history'),
                             [self.toolbar.rewind,
                              self.toolbar.undo_action,
                              self.toolbar.redo_action
                              ]
                           ),
                         self.toolbar.toggle_lean_editor_action,
                         self.toolbar.change_exercise_action
                          ])

        # ─────────────────────── Main Menu ─────────────────────── #
        outline = [menu_deaduction, menu_exercise]
        menu_bar = MenuBar(self, outline)
        self.setMenuBar(menu_bar)

    def closeEvent(self, event: QEvent):
        """
        Overload native Qt closeEvent method — which is called when self
        is closed — to send the signal self.window_closed.

        :param event: Some Qt mandatory thing.
        """
        log.info("Closing ExerciseMainWindow")

        # Close children
        self.lean_editor.close()
        self.proof_outline_window.close()

        # Save window geometry
        settings = QSettings("deaduction")
        settings.setValue("emw/Geometry", self.saveGeometry())

        if self.close_coordinator:
            # Set up by Coordinator
            self.close_coordinator()

        self.window_closed.emit()

        super().closeEvent(event)
        self.deleteLater()

    ##################
    # Config methods #
    ##################

    def open_config_window(self):
        """
        Open the preference window.
        """
        window = ConfigMainWindow(parent=self)
        window.applied.connect(self.apply_new_settings)
        window.show()

    @Slot()
    def apply_new_settings(self, modified_settings):
        """
        This is where UI is updated when preferences are modified.
        """
        log.debug("New settings: ")
        log.debug(modified_settings)
        if modified_settings:
            self.current_selection = []
            # TODO: only for relevant changes in preferences
            # TODO: try more subtle updating...
            ##############################
            # Redefine ecw from scratch! #
            ##############################
            self.ecw = ExerciseCentralWidget(self.exercise)
            self.setCentralWidget(self.ecw)
            self.__connect_signals()
            if not self.freezed:  # If freezed then maybe goal has not been set
                self.ecw.update_goal(
                                 self.current_goal,
                                 self.displayed_proof_step.current_goal_number,
                                 self.displayed_proof_step.total_goals_counter)
            self.toolbar.update()
            self.__init_menubar()
            # Reconnect Context area signals and slots
            self.ecw.objects_wgt.clicked.connect(self.process_context_click)
            self.ecw.props_wgt.clicked.connect(self.process_context_click)

            # self.ecw.target_wgt.mouseReleaseEvent = self.process_target_click
            if hasattr(self.ecw, "action_apply_button"):
                self.ecw.objects_wgt.apply_math_object_triggered.connect(
                    self.apply_math_object_triggered)
                self.ecw.props_wgt.apply_math_object_triggered.connect(
                    self.apply_math_object_triggered)

        self.ecw.target_wgt.mark_user_selected(self.target_selected)

    ######################
    ######################
    # Properties or like #
    ######################
    ######################

    @property
    def target_selected_by_default(self):
        return cvars.get('functionality.target_selected_by_default', False) \
                or self.test_mode or self.automatic_action

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

    def pretty_current_selection(self) -> str:
        """
        Return the current selection as a string, for display.

        :return: See above.
        """
        msg = 'Current user selection: '
        msg += str([item.text() for item in self.current_selection])

        return msg

    # ─────────────────── Logical information ─────────────────── #

    @property
    def logically_previous_proof_step(self):
        """
        The previous proof step in the logical order is always stored in the
        previous entry of lean_file's history. This is NOT the proof step
        that was previously displayed by the ui in case of history undo or
        rewind (which is stored in self.displayed_proof_step).
        """
        if self.lean_file:
            return self.lean_file.previous_proof_step
        else:
            return None

    @property
    def objects(self):
        """ MathObject's instances displayed as objects"""
        return [item.math_object for item in self.ecw.objects_wgt.items]

    @property
    def properties(self):
        """ MathObject's instances displayed as properties"""
        return [item.math_object for item in self.ecw.props_wgt.items]

    @property
    def current_selection_as_mathobjects(self):
        """
        Do not delete, used many times! Return the current selection as
        an ordered list of instances of the class MathObject directly.

        :return: See above.
        """
        return [item.math_object for item in self.current_selection]

    # ─────────────────── Conversion methods ─────────────────── #

    def button_from_string(self, string: str):
        """
        Search a button widget that match string.
        Search successively in
        - ActionButton,
        - history buttons
        """
        # TODO: add search in context widgets.
        button = self.ecw.action_button(string)
        if button:
            return button
        history_buttons = {'undo': self.toolbar.undo_action,
                           'redo': self.toolbar.redo_action,
                           'rewind': self.toolbar.rewind}
        if string.find('undo') != -1:
            string = 'undo'
        elif string.find('redo') != -1:
            string = 'redo'
        elif string.find('rewind') != -1:
            string = 'rewind'
        if string in history_buttons:
            return history_buttons[string]
        log.warning(f"No button found from {string}")

    def context_item_from_math_object(self, math_object):
        """
        Turn a MathObject into a MathObjectWidgetItem of the context.
        """
        if math_object.math_type.is_prop():
            item = self.ecw.props_wgt.item_from_logic(math_object)
        else:
            item = self.ecw.objects_wgt.item_from_logic(math_object)
        return item

    def context_item_from_string(self, name):
        """
        Turn a string, as used in AutoStep, into a MathObjectWidgetItem
        of the context.
        """
        item = None
        if name.startswith('@O'):
            try:
                nb = int(name[2:]) - 1
                item = self.ecw.objects_wgt.item_from_nb(nb)
            except IndexError:
                pass
        elif name.startswith('@P'):
            try:
                nb = int(name[2:]) - 1
                item = self.ecw.props_wgt.item_from_nb(nb)
            except IndexError:
                pass
        else:
            if name.startswith('@'):  # (unwanted @)
                name = name[1:]
            math_object = self.current_goal.math_object_from_name(name)
            if math_object:
                item = self.context_item_from_math_object(math_object)
        return item
    
    def contextualised_selection(self, selection: [Union[MathObject, str]]):
        """
        Turn ContextMathObject or str in the list into MathObjectWidgetItem.
        """

        contextualised_selection = []
        for item in selection:
            if isinstance(item, str):
                item = self.context_item_from_string(item)
            elif isinstance(item, MathObject):
                item = self.context_item_from_math_object(item)
            contextualised_selection.append(item)
        return contextualised_selection

    def contextualised_button(self, button):
        """Turn an action encoded by a string, e.g. "forall", into a button."""

        contextualised_action = button
        if isinstance(button, str):
            contextualised_action = self.button_from_string(button)
        return contextualised_action

    ##############
    ##############
    # UI Methods #
    ##############
    ##############

    @Slot()
    def statement_triggered_filter(self, item: Union[StatementsTreeWidgetItem,
                                                     StatementsTreeWidgetNode]
                                   ):
        """
        Emit statement_triggered iff the clicked item is not a node,
        i.e. corresponds to a statement.
        """
        if isinstance(item, StatementsTreeWidgetItem):
            self.statement_triggered.emit(item)

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
        self.freezed = yes
        self.ecw.freeze(yes)
        self.toolbar.setEnabled(not yes)
        if yes:
            self.statusBar.cancel_pending_msgs()

    def history_button_unfreeze(self, at_beginning, at_end):
        """
        Unfreeze the relevant history btns.
        """
        self.toolbar.undo_action.setEnabled(not at_beginning)
        self.toolbar.rewind.setEnabled(not at_beginning)
        self.toolbar.redo_action.setEnabled(not at_end)

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

    @Slot(MathObjectWidgetItem)
    def process_context_click(self, item: Union[QModelIndex,
                                                MathObjectWidgetItem]):
        """
        Add or remove item (item represents a math. object or property)
        from the current selection, depending on whether it was already
        selected or note.

        :item: The math. object or property user just clicked on.
        """
        # TODO: allow simultaneous selection of target and context objects
        if isinstance(item, QModelIndex):
            index = item
            item = self.ecw.objects_wgt.item_from_index(index)
            if not item:
                item = self.ecw.props_wgt.item_from_index(index)
        # Once clicked, one does not want the item to remain visually
        # selected
        # item.setSelected(False)
        # Un-select target
        self.ecw.target_wgt.mark_user_selected(False)
        self.target_selected = False

        if item not in self.current_selection:
            item.mark_user_selected(True)
            self.current_selection.append(item)
        elif item is not self.double_clicked_item:
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

    def simulate_selection(self,
                           selection:
                           [Union[MathObject, MathObjectWidgetItem]]):
        """
        Simulate user selecting selection: for every item in selection,
        self.process_context_click(item).
        Note that items in selection are first transformed into
        MathObjectWidgetItem if they are MathObject.
        """
        self.current_selection = []
        for item in selection:
            if isinstance(item, MathObject):
                if item.math_type.is_prop():
                    item = self.ecw.props_wgt.item_from_logic(item)
                else:
                    item = self.ecw.objects_wgt.item_from_logic(item)
            self.process_context_click(item)

        # Select target if no selection:
        if not self.current_selection:
            self.process_target_click(None)

    async def simulate(self, proof_step: ProofStep, duration=0.4):
        """
        Simulate proof_step by selecting the selection and
        checking button or statement stored in proof_step. This is called
        when redoing, but also when processing automatic actions, or testing.
        Note that contrarily to what happens in self.simulate_user_action,
        the corresponding actions are NOT processed,
        since this would modify history of the lean_file which is not what
        we want when redoing.
        The method is asynchronous because we wait for the button blinking.
        """

        self.simulate_selection(proof_step.selection)
        # Check button or statement
        if isinstance(proof_step.button, ActionButton):
            self.ecw.freeze(False)
            await proof_step.button.simulate(duration=duration)
            self.ecw.freeze(self.freezed)
        elif isinstance(proof_step.statement_item, StatementsTreeWidgetItem):
            await proof_step.statement_item.simulate(duration=duration)

    async def simulate_user_action(self,
                                   user_action: UserAction,
                                   duration=0.4) -> (bool, str):
        """
        Simulate user_action as if buttons were actually pressed.
        Return True if the simulation was actually performed, and False with
        a detailed msg if not (useful for testing).
        This is called by Coordinator.process_automatic_actions.
        """
        log.debug("Simulating user action...")
        msg = ""
        msg += f"    -> selection = {user_action.selection}"
        selection = self.contextualised_selection(user_action.selection)
        if None in selection:
            msg += "    -> (None in selection: "
            for item in selection:
                if isinstance(item, MathObject):
                    msg += item.to_display()
                elif isinstance(item, str):
                    msg += item
                else:
                    msg += str(item)
            msg += ')' + '\n'
            msg += self.current_goal.to_tooltip()
            msg += f'\n {len(self.objects)} objects, {len(self.properties)} ' \
                   f'properties.'
            return False, msg
        self.simulate_selection(selection)
        self.user_input = user_action.user_input

        button = user_action.button
        statement = user_action.statement
        if button:
            msg += f"    -> click on button {button}"
            action_button = self.contextualised_button(button)
            if action_button:
                self.ecw.freeze(False)
                await action_button.simulate(duration=duration)
                action_button.click()
                self.ecw.freeze(self.freezed)
                return True, msg
            else:
                return False, f"No button match {button}"
        elif statement:
            msg += f"    -> statement {statement} called"
            statement_widget = self.ecw.statements_tree.from_name(statement)
            if statement_widget:
                self.statement_triggered.emit(statement_widget)
                await statement_widget.simulate(duration=0.4)
                return True, msg
            else:
                return False, f"No statement match {statement}"

        msg += "    ->(No button nor statement found)"
        return False, msg

    ##################
    ##################
    # Update methods #
    ##################
    ##################

    @Slot()
    def update_lean_editor(self, lean_file_content):
        """
        Update the L∃∀N editor widget to that of the current virtual
        file L∃∀N code.
        """

        self.lean_editor.code_set(lean_file_content)

    def display_current_goal_solved(self, delta):
        proof_step = self.lean_file.current_proof_step
        if proof_step.current_goal_number and not self.test_mode \
                and self.lean_file.current_number_of_goals \
                and not proof_step.is_error() \
                and not proof_step.is_undo():
            log.info(f"Current goal solved!")
            if delta == -1:
                message = _('Current goal solved')
            else:  # Several goals solved at once ??
                nb = str(-delta)
                message = nb + ' ' + _('goals solved!')
            QMessageBox.information(self, '', message, QMessageBox.Ok)

    def manage_msgs(self, proof_step):
        """
        Display msgs in status bar, "current goal solved" msg if needed,
        and display proof_outline in proof_outline_window.
        """
        # Display current goal solved
        if not proof_step.is_error() and not proof_step.is_history_move():
            if proof_step.delta_goals_count < 0:
                self.display_current_goal_solved(proof_step.delta_goals_count)

        # Status bar
        if not proof_step.is_history_move():
            self.statusBar.manage_msgs(proof_step)
        elif proof_step.is_redo() or proof_step.is_goto():
            self.statusBar.manage_msgs(self.lean_file.current_proof_step)

        # Update proof_outline_window
        powt = self.proof_outline_window.tree
        if proof_step.is_history_move():
            powt.set_marked(self.lean_file.target_idx-1)
        elif proof_step.is_error():
            powt.delete_after_goto_and_error(proof_step)
        else:
            powt.delete_and_insert(proof_step)

    def process_wrong_user_input(self):
        self.empty_current_selection()  # That's it?? Is this even useful??

    def update_goal(self, new_goal):
        """
        Change widgets (target, math. objects and properties) to
        new_goal and update internal mechanics accordingly.

        :param new_goal: The new Goal to update / set the interface to.
        (or None if it has not been received yet).
        """
        # TODO: tags will be incorporated in ContextMathObjects
        log.info("Updating UI")
        self.manage_msgs(self.displayed_proof_step)
        self.user_input = []

        if not new_goal or new_goal is self.current_goal:  # No update needed
            return

        # Get previous goal and set tags
        # if self.logically_previous_proof_step:
        #     # Fixme: not when undoing history ?
        #     previous_goal = self.logically_previous_proof_step.goal
        #     Goal.compare(new_goal, previous_goal)  # Set tags

        # Reset current context selection
        # Here we do not use empty_current_selection since Widgets may have
        # been deleted, and anyway this is cosmetics since  widgets are
        # destroyed and re-created by "self.ecw.update_goal" just below
        self.current_selection = []

        # Update UI and attributes. Target stay selected if it was.
        # statements_scroll = self.ecw.statements_tree.verticalScrollBar(
        #                                                            ).value()
        self.ecw.update_goal(new_goal,
                             self.displayed_proof_step.current_goal_number,
                             self.displayed_proof_step.total_goals_counter)
        self.ecw.target_wgt.mark_user_selected(self.target_selected)
        self.current_goal = new_goal

        # Reconnect Context area signals and slots
        self.ecw.objects_wgt.clicked.connect(self.process_context_click)
        self.ecw.props_wgt.clicked.connect(self.process_context_click)

        # self.ecw.target_wgt.mouseReleaseEvent = self.process_target_click
        if hasattr(self.ecw, "action_apply_button"):
            self.ecw.objects_wgt.apply_math_object_triggered.connect(
                self.apply_math_object_triggered)
            self.ecw.props_wgt.apply_math_object_triggered.connect(
                self.apply_math_object_triggered)


