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
from typing import    Union, Optional, Any

from PySide2.QtCore    import (Signal,
                               Slot,
                               QEvent,
                               QSettings,
                               QModelIndex,
                               QTimer)

from PySide2.QtGui import QColor

from PySide2.QtWidgets import (QMainWindow,
                               QMessageBox,
                               QAction)

from deaduction.pylib.coursedata        import  Exercise, UserAction
from deaduction.pylib.mathobj           import (MathObject,
                                                ProofStep)
from deaduction.pylib.math_display.pattern_init import pattern_init

from deaduction.dui.primitives          import deaduction_fonts

from deaduction.dui.elements            import (ActionButton,
                                                LeanEditor,
                                                StatementsTreeWidgetItem,
                                                StatementsTreeWidgetNode,
                                                MathObjectWidget,
                                                MathObjectWidgetItem,
                                                MenuBar,
                                                MenuBarAction,
                                                ConfigMainWindow,
                                                ProofOutlineWindow,
                                                ProofTreeController,
                                                HelpWindow)
from ._exercise_main_window_widgets     import (ExerciseCentralWidget,
                                                ExerciseStatusBar,
                                                ExerciseToolBar,
                                                GlobalToolbar)

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
    cancel_server                = Signal()

    # User action signals:
    action_triggered             = Signal(ActionButton)
    # apply_math_object_triggered  = Signal(MathObjectWidget)
    statement_triggered          = Signal(StatementsTreeWidgetItem)
    statement_dropped            = Signal(StatementsTreeWidgetItem)
    math_object_dropped          = Signal(MathObjectWidgetItem,
                                          MathObjectWidgetItem)

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
        # self.current_selection    = []
        self._target_selected     = False
        self.user_input           = []
        # self.double_clicked_item  = None
        self.freezed              = False

        # ─────────────────────── Elements ─────────────────────── #

        self.ecw                  = ExerciseCentralWidget(exercise)
        self.lean_editor          = LeanEditor()
        self.exercise_toolbar              = ExerciseToolBar()
        self.global_toolbar       = GlobalToolbar()
        self.proof_outline_window = ProofOutlineWindow()
        self.proof_tree_controller= ProofTreeController()
        self.statusBar            = ExerciseStatusBar(self)
        self.config_window        = None
        self.help_window = HelpWindow()
        self.close_help_window_timer = QTimer()
        self.close_help_window_timer.setSingleShot(True)

        # ─────────────────────── UI ─────────────────────── #

        self.setCentralWidget(self.ecw)
        self.addToolBar(self.exercise_toolbar)
        self.addToolBar(self.global_toolbar)
        self.proof_tree_controller.proof_tree_window.action = \
            self.exercise_toolbar.toggle_proof_tree
        self.proof_outline_window.action = \
            self.exercise_toolbar.toggle_proof_outline_action
        self.lean_editor.action = \
            self.exercise_toolbar.toggle_lean_editor_action
        self.help_window.action = \
            self.exercise_toolbar.toggle_help_action
        if self.proof_tree_window.isVisible():
            self.exercise_toolbar.toggle_proof_tree.setChecked(True)

        self.exercise_toolbar.redo_action.setEnabled(False)  # No history at beg
        self.exercise_toolbar.undo_action.setEnabled(False)  # same
        self.exercise_toolbar.rewind.setEnabled(False)  # same
        self.exercise_toolbar.go_to_end.setEnabled(False)  # same
        self.__init_menubar()
        self.setStatusBar(self.statusBar)
        self.__connect_signals()
        self.__connect_toolbar_signals()

        # Restore geometry
        settings = QSettings("deaduction")
        geometry = settings.value("emw/Geometry")
        # maximised = settings.value("emw/isMaximised")
        # log.debug(f"maximised: {maximised}")
        if geometry:
            self.restoreGeometry(geometry)
            # if maximised:  # FIXME: Does not work on Linux?!
            # self.showMaximized()
        # proof_tree_is_visible = settings.value("emw/ShowProofTree")
        # if proof_tree_is_visible:
        #     print("Proof tree was shown")
        #     QTimer.singleShot(500,
        #                       self.exercise_toolbar.toggle_proof_tree.toggle)
            # self.exercise_toolbar.toggle_proof_tree.toggle()
            # self.exercise_toolbar.toggle_proof_tree.setChecked(True)
        self.close_coordinator = None  # Method set up by Coordinator

        # 1s to allow correct geometry(?) Does not work
        # QTimer.singleShot(1000, self.__init_help_window)
        self.freeze()  # Wait for data before allowing user actions.

    #######################
    # Init /close methods #
    #######################
    def __init_menubar(self):
        """
        Create ExerciseMainWindow's menubar. Relevant classes are MenuBar,
        MenuBarAction and MenuBarMenu, from deaduction.dui.elements.
        """
        # ─────────────────────── Submenus ─────────────────────── #
        menu_deaduction = (_("Preferences"),
                           [self.global_toolbar.settings_action])

        menu_exercise = (_('Exercise'),
                         [(_('Exercise history'),
                             [self.exercise_toolbar.rewind,
                              self.exercise_toolbar.undo_action,
                              self.exercise_toolbar.redo_action,
                              self.exercise_toolbar.go_to_end,
                              self.exercise_toolbar.toggle_proof_outline_action,
                              self.exercise_toolbar.toggle_proof_tree
                              ]),
                         self.exercise_toolbar.toggle_help_action,
                         self.exercise_toolbar.toggle_lean_editor_action,
                         self.global_toolbar.change_exercise_action])

        # ─────────────────────── Main Menu ─────────────────────── #
        outline = [menu_deaduction, menu_exercise]
        menu_bar = MenuBar(self, outline)
        self.setMenuBar(menu_bar)

    def __connect_signals(self):
        """
        Connect all signals. Called at init. SOme signals are connected in
        update_goal.
        """
        log.debug("EMW: connect signals")
        # Actions area
        for action_button in self.ecw.actions_buttons:
            action_button.action_triggered.connect(self.action_triggered)
        self.ecw.statements_tree.itemClicked.connect(
                                            self.statement_triggered_filter)

        # Context area
        self.ecw.props_wgt.statement_dropped.connect(self.statement_dropped)
        self.ecw.props_wgt.math_object_dropped.connect(self.math_object_dropped)
        self.ecw.objects_wgt.math_object_dropped.connect(
            self.math_object_dropped)
        self.ecw.statements_tree.math_object_dropped.connect(
            self.statement_triggered)
        # self.ecw.objects_wgt.clicked.connect(self.process_context_click)
        # self.ecw.props_wgt.clicked.connect(self.process_context_click)

        # # UI
        # self.exercise_toolbar.toggle_lean_editor_action.triggered.connect(
        #         self.lean_editor.toggle)
        # self.exercise_toolbar.toggle_proof_outline_action.triggered.connect(
        #         self.proof_outline_window.toggle)
        # self.exercise_toolbar.toggle_proof_tree.triggered.connect(
        #         self.proof_tree_window.toggle)
        # self.exercise_toolbar.toggle_help_action.triggered.connect(
        #     self.show_help_on_item)
        # self.global_toolbar.change_exercise_action.triggered.connect(
        #                                             self.change_exercise)
        # self.global_toolbar.settings_action.triggered.connect(
        #                                             self.open_config_window)
        # self.ecw.target_wgt.target_label.mousePressEvent = \
        #     self.process_target_click

        # Double clicks (help)
        self.ecw.objects_wgt.doubleClicked.connect(
                                            self.process_context_double_click)
        self.ecw.props_wgt.doubleClicked.connect(
                                            self.process_context_double_click)

        target_lbl = self.ecw.target_wgt.target_label
        target_lbl.clicked.connect(self.process_target_click)
        target_lbl.double_clicked.connect(self.process_target_double_click)
        self.close_help_window_timer.timeout.connect(self.help_window.hide)

        # All context clicks, including target_lbl --> self.contest_clicked
        self.ecw.objects_wgt.clicked.connect(self.context_clicked)
        self.ecw.props_wgt.clicked.connect(self.context_clicked)
        target_lbl.clicked.connect(self.context_clicked)

    # def __init_help_window(self):
    #     gl_geo = global_geometry(self.ecw,
    #                              self.ecw.statements_tree.geometry())
    #     # self.help_window.set_geometry(gl_geo)

    def __connect_toolbar_signals(self):
        self.exercise_toolbar.toggle_lean_editor_action.triggered.connect(
                self.lean_editor.toggle)
        self.exercise_toolbar.toggle_proof_outline_action.triggered.connect(
                self.proof_outline_window.toggle)
        self.exercise_toolbar.toggle_proof_tree.triggered.connect(
                self.proof_tree_window.toggle)
        self.exercise_toolbar.toggle_help_action.triggered.connect(
            self.show_help_on_item)
        self.global_toolbar.change_exercise_action.triggered.connect(
                                                    self.change_exercise)
        self.global_toolbar.settings_action.triggered.connect(
                                                    self.open_config_window)
        self.global_toolbar.stop.triggered.connect(self.stop)

    def close_help_window(self):
        if self.help_window.isVisible():
            self.close_help_window_timer.start(200)

    @Slot()
    def context_clicked(self):
        """
        Almost any click should close the help window.
        """
        self.close_help_window()

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
        self.proof_tree_window.close()
        self.help_window.close()

        # Save window geometry
        # FIXME: does not work
        settings = QSettings("deaduction")
        is_maximised = self.isMaximized()
        log.debug(f"Maximised: {is_maximised}")
        settings.setValue("emw/isMaximised", is_maximised)
        self.showNormal()
        settings.setValue("emw/Geometry", self.saveGeometry())
        settings.setValue("emw/ShowProofTree",
                          self.proof_tree_window.isVisible())

        if self.close_coordinator:
            # Set up by Coordinator
            self.close_coordinator()

        self.window_closed.emit()
        # event.accept()  # THIS creates crash after the second closing!!
        super().closeEvent(event)
        self.deleteLater()

    def set_msgs_for_status_bar(self, proof_msg: callable):
        self.statusBar.proof_msg = proof_msg

    ##################
    # Config methods #
    ##################

    def open_config_window(self):
        """
        Open the preference window.
        """
        if not self.config_window or self.config_window.isHidden():
            self.config_window = ConfigMainWindow(parent=self)
            self.config_window.applied.connect(self.apply_new_settings)
        self.config_window.show()
        self.close_help_window()

    @Slot()
    def apply_new_settings(self, modified_settings):
        """
        This is where UI is updated when preferences are modified.
        """
        log.debug("New settings: ")
        log.debug(modified_settings)
        update_ecw_display = False
        while modified_settings:
            setting = modified_settings.pop()
            # (1) DnD
            if setting in ('functionality.drag_statements_to_context',
                           'functionality.drag_and_drop_in_context',
                           'functionality.drag_context_to_statements'):
                self.ecw.set_drag_and_drop_config()
                log.info("New DnD settings")
            # (2) Fonts
            elif setting in ("display.target_font_size",
                             "display.main_font_size",
                             "display.statements_font_size",
                             "display.tooltips_font_size",
                             'display.math_font_file',
                             'display.proof_tree_font_size'):
                log.info("New fonts settings")
                deaduction_fonts.set_fonts()
            elif setting == "display.target_display_on_top":
                self.ecw.organise_main_layout()
            elif setting in (
                    "symbols_AND_OR_NOT_IMPLIES_IFF_FORALL_EXISTS_EQUAL_MAP",
                    'display.use_symbols_for_logic_button',
                    'display.font_size_for_symbol_buttons'):
                self.ecw.set_font()
            elif setting == 'functionality.allow_implicit_use_of_definitions':
                self.ecw.statements_tree.update_tooltips()
            elif setting == "logic.use_bounded_quantification_notation":
                pattern_init()
                update_ecw_display = True
            else:  # Setting has not been handled, force update display
                update_ecw_display = True
                # break
        # Case of unhandled settings:
        # if not updated:  # Last popped setting has not been handled
        #     modified_settings.append(setting)

        if update_ecw_display:
            log.info("New ecw...")
            # self.current_selection = []
            # self.empty_current_selection()
            # TODO: only for relevant changes in preferences
            # TODO: try more subtle updating...
            ##############################
            # Redefine ecw from scratch! #
            ##############################
            # if 'display.math_font_file' in modified_settings:
            # deaduction_fonts.set_fonts()

            self.ecw = ExerciseCentralWidget(self.exercise)
            self.setCentralWidget(self.ecw)
            self.__connect_signals()
            if not self.freezed:  # If freezed then maybe goal has not been set
                self.ecw.update_goal(self.current_goal, self.pending_goals)
            self.exercise_toolbar.update()
            self.__init_menubar()

            # self.ecw.target_wgt.target_label.mousePressEvent = \
            #     self.process_target_click
            # if hasattr(self.ecw, "action_apply_button"):
            #     self.ecw.objects_wgt.apply_math_object_triggered.connect(
            #         self.apply_math_object_triggered)
            #     self.ecw.props_wgt.apply_math_object_triggered.connect(
            #         self.apply_math_object_triggered)

        # self.ecw.target_wgt.mark_user_selected(self.target_selected)

    ######################
    ######################
    # Properties or like #
    ######################
    ######################

    @property
    def proof_tree_window(self):
        return self.proof_tree_controller.proof_tree_window

    @property
    def target_selected(self):
        """
        Boolean, True iff target is selected.
        """
        # Fixme: obsolete
        # if not self.target_selected_by_default:
        #     return self._target_selected
        # else:
        #     # Target is selected by default if current_selection is empty
        #     return not self.current_selection
        return self._target_selected

    @target_selected.setter
    def target_selected(self, target_selected):
        self._target_selected = target_selected
        self.ecw.target_wgt.mark_user_selected(self.target_selected)
        # print(f"Target selected :{self._target_selected}")

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
    def pending_goals(self):
        """
        Return the list of unsolved goals, excluding the current goal. If
        some history moves occurred, then the part of the proof after the
        displayed step is ignored.
        """

        # self.proof_tree_controller.proof_tree.set_truncate_mode(True)
        pgn = self.proof_tree_controller.proof_tree.pending_goal_nodes()
        # self.proof_tree_controller.proof_tree.set_truncate_mode(False)

        return pgn

        # proof_tree = self.proof_tree_controller.proof_tree
        # # gn = proof_tree.current_goal_node.goal_nb
        # # BEWARE, here we must use historic proof_step,
        # # NOT self.displayed_proof_step which is the latest proof_step,
        # # maybe a history move, and has the greatest proof_step_nb!
        # pf_nb = self.lean_file.current_proof_step.pf_nb
        # pgs = [gn.goal for gn in proof_tree.pending_goal_nodes(
        #        till_proof_step_nb=pf_nb)]
        # # if proof_tree.is_at_end():
        # #     pgs = [gn.goal for gn in proof_tree.pending_goal_nodes()]
        # # else:
        # #     pgs = []
        # return pgs

    @property
    def current_selection(self):
        """
        Note that the selection is not ordered by click time.
        """
        sel_objs = self.ecw.objects_wgt.selected_items()
        sel_props = self.ecw.props_wgt.selected_items()
        return sel_objs + sel_props

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

        :return: ActionButton or None
        """
        # FIXME: obsolete
        # TODO: add search in context widgets.
        button = self.ecw.action_button(string)
        if button:
            return button
        history_buttons = {'undo': self.exercise_toolbar.undo_action,
                           'redo': self.exercise_toolbar.redo_action,
                           'rewind': self.exercise_toolbar.rewind,
                           'go_to_end': self.exercise_toolbar.go_to_end}
        if string.find('undo') != -1:
            string = 'undo'
        elif string.find('redo') != -1:
            string = 'redo'
        elif string.find('rewind') != -1:
            string = 'rewind'
        elif string.find('end') != -1:
            string = 'go_to_end'
        if string in history_buttons:
            return history_buttons[string]
        log.warning(f"No button found from {string}")

    def context_item_from_math_object(self, math_object) -> \
            MathObjectWidgetItem:
        """
        Turn a MathObject into a MathObjectWidgetItem of the context.
        """
        if math_object.math_type.is_prop():
            item = self.ecw.props_wgt.item_from_logic(math_object)
        else:
            item = self.ecw.objects_wgt.item_from_logic(math_object)
        return item

    def context_item_from_string(self, name) -> MathObjectWidgetItem:
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
    
    def contextualised_selection(self, selection: [Union[MathObject, str]])\
            -> [MathObjectWidgetItem]:
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
        log.debug(contextualised_selection)
        return contextualised_selection

    @staticmethod
    def contextualised_button(button_name: str) -> ActionButton:
        """Turn an action encoded by a string, e.g. "forall", into a button.
        """
        return ActionButton.from_name.get(button_name)

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
        self.exercise_toolbar.setEnabled(not yes)
        # if yes:
        #     self.statusBar.cancel_pending_msgs()

    def history_button_unfreeze(self, at_beginning, at_end):
        """
        Unfreeze the relevant history btns.
        """
        self.exercise_toolbar.undo_action.setEnabled(not at_beginning)
        self.exercise_toolbar.rewind.setEnabled(not at_beginning)
        self.exercise_toolbar.redo_action.setEnabled(not at_end)
        self.exercise_toolbar.go_to_end.setEnabled(not at_end)

    @Slot()
    def empty_current_selection(self):
        """
        Clear current (user) selection of math. objects and properties.
        """

        # for item in self.current_selection:
        #     item.mark_user_selected(False)
        # self.current_selection = []
        self.ecw.props_wgt.clearSelection()
        self.ecw.objects_wgt.clearSelection()

    # @Slot(MathObjectWidgetItem)
    # def process_context_click(self, item: Union[QModelIndex,
    #                                             MathObjectWidgetItem]):
    #     """
    #     Add or remove item (item represents a math. object or property)
    #     from the current selection, depending on whether it was already
    #     selected or note.
    #
    #     :item: The math. object or property user just clicked on.
    #     """
    #
    #     if isinstance(item, QModelIndex):
    #         index = item
    #         item = self.ecw.objects_wgt.item_from_index(index)
    #         if not item:
    #             item = self.ecw.props_wgt.item_from_index(index)
    #
    #     if item not in self.current_selection:
    #         # item.mark_user_selected(True)
    #         self.current_selection.append(item)
    #     else:
    #         # elif item is not self.double_clicked_item:
    #         # item.mark_user_selected(False)
    #         self.current_selection.remove(item)

        # Clear selection (we do not use the QListView selection mechanism):
        # self.ecw.props_wgt.clearSelection()
        # self.ecw.objects_wgt.clearSelection()

    @Slot()
    def process_target_click(self, event=None, on=None):
        """
        Select or un-select target. Note that self.target_selected's setter
        automatically call mark_user_selected().
        """
        self.target_selected = not self.target_selected if on is None else on

    @Slot()
    def show_help_on_item(self, item=None, on_target=False):
        """
        Show help on item if any, or on selected context object or target if
        there is a single selected object
        """

        toggle = False
        if not item:
            if self.help_window.isVisible():  # Click from icon, close window
                self.help_window.toggle(False)
                return
        else:
            obj = self.displayed_proof_step.context_obj_solving
            self.help_window.set_math_object(item, on_target=on_target,
                                             context_solving=obj)

        self.help_window.toggle(True)

    @Slot(MathObjectWidgetItem)
    def process_context_double_click(self, index):
        """
        Call the help window on double-clicked context item.
        """

        # Stop closing process, and unselect everything
        self.close_help_window_timer.stop()
        self.empty_current_selection()
        self.process_target_click(on=False)

        # Find item from index, in props_wgt or objects_wgt
        props_wgt = self.ecw.props_wgt
        math_item: MathObjectWidgetItem = props_wgt.item_from_index(index)
        if not math_item:
            obj_wgt = self.ecw.objects_wgt
            math_item = obj_wgt.item_from_index(index)

        if math_item:
            self.show_help_on_item(item=math_item)
            # self.help_window.set_math_object(math_item)
            # self.help_window.toggle(True)

    @Slot()
    def process_target_double_click(self, event=None):

        # Stop closing process, and unselect everything
        self.close_help_window_timer.stop()
        self.empty_current_selection()
        self.process_target_click(on=False)

        # target = self.ecw.target_wgt.target
        math_item = self.ecw.target_wgt.target_label
        self.show_help_on_item(item=math_item, on_target=True)
        # self.help_window.set_math_object(item, target=True)
        # self.help_window.toggle(True)

    def simulate_selection(self,
                           selection:
                           [Union[MathObject, MathObjectWidgetItem]],
                           target_selected: bool):
        """
        Simulate user selecting selection: for every item in selection,
        self.process_context_click(item).
        Note that items in selection are first transformed into
        MathObjectWidgetItem if they are MathObject.
        """

        self.empty_current_selection()
        for item in selection:
            # Determine math_object and MathWidgetItem
            if isinstance(item, MathObject):
                math_object = item
                item: MathObjectWidgetItem = \
                    MathObjectWidgetItem.from_math_object(item)

            item.select()

        if target_selected:
            self.process_target_click()

    async def simulate_user_action(self,
                                   user_action: UserAction,
                                   duration=0.4,
                                   execute_action=True) -> (bool, str):
        """
        Simulate user_action as if buttons were actually pressed.
        Return True if the simulation was actually performed, and False with
        a detailed msg if not (useful for testing).
        This is called by Coordinator.process_automatic_actions.
        If execute_action is True then the action is actually executed,
        as if usr had press the button.
        If not, the UI just shows buttons blinking ; this is used
        when history_redo is executed, to keep all the following history.
        """
        log.debug("Simulating user action...")
        msg = ""
        msg += f"    -> selection = {user_action.selection}"
        selection = self.contextualised_selection(user_action.selection)
        target_selected = user_action.target_selected
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
        self.simulate_selection(selection, target_selected)
        self.user_input = user_action.user_input

        button = user_action.button_name
        statement_name = user_action.statement_name
        if button:
            msg += f"    -> click on button {button}"
            action_button = self.contextualised_button(button)
            if action_button:
                self.ecw.freeze(False)
                await action_button.simulate(duration=duration)
                if execute_action:  # Execute the action!
                    action_button.click()
                self.ecw.freeze(self.freezed)
                return True, msg
            else:
                return False, f"No button match {button}"
        elif statement_name:
            msg += f"    -> statement {statement_name} called"
            statement_widget = \
                StatementsTreeWidgetItem.from_end_of_lean_name(statement_name)
            if statement_widget:
                if execute_action:  # Execute the action!
                    self.statement_triggered.emit(statement_widget)
                await statement_widget.simulate(duration=duration)
                return True, msg
            else:
                return False, f"No statement match {statement_name}"

        msg += "    ->(No button nor statement found)"
        return False, msg

    async def simulate(self, proof_step: ProofStep, duration=0.4):
        """
        Simulate proof_step by selecting the selection and
        checking button or statement stored in proof_step. This is called
        when redoing, but also when processing automatic actions, or testing.
        Note that the corresponding actions are NOT processed,
        since this would modify history of the lean_file which is not what
        we want when redoing.
        The method is asynchronous because we wait for the button blinking.
        """

        user_action = UserAction.from_proof_step(proof_step)
        # log.info("Simulating proof_step with:")
        # print(user_action)
        success, msg = await self.simulate_user_action(user_action, duration,
                                                       execute_action=False)
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

        log.info("Updating UI")
        if self.help_window.isVisible():
            self.help_window.toggle(yes=False)
        self.proof_tree_controller.update()
        self.manage_msgs(self.displayed_proof_step)
        self.user_input = []

        # Reset current context selection
        # Here we do not use empty_current_selection since Widgets may have
        # been deleted, and anyway this is cosmetics since  widgets are
        # destroyed and re-created by "self.ecw.update_goal" just below
        self.target_selected = False
        # self.current_selection = []
        self.empty_current_selection()

        if not new_goal or new_goal is self.current_goal:  # No update needed
            return

        # Update UI and attributes. Target stay selected if it was.
        # statements_scroll = self.ecw.statements_tree.verticalScrollBar(
        #                                                            ).value()
        self.ecw.update_goal(new_goal, self.pending_goals)
        # self.ecw.target_wgt.mark_user_selected(self.target_selected)
        self.current_goal = new_goal

        # NB: there seems to be a bug in Qt,
        #  self.ecw.target_wgt.mousePressEvent is not called when
        #  self.ecw.target_wgt.target_label format is set to richText (!)
        #  so we call the event of the target_label instead.
        # self.ecw.target_wgt.target_label.mousePressEvent = \
        #     self.process_target_click

