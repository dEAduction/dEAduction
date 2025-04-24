"""
#########################################################
# exercise_widget.py : provide ExerciseMainWindow parts #
#########################################################

    Provide classes:
        - ExerciseStatusBar,
        - ExerciseToolbar,
        - ExerciseCentralWidget.
    The class ExerciseMainWindow is not in this module.

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

import                          logging

from typing import Optional

from PySide2.QtCore import    ( Slot,
                                QTimer,
                                Qt)

from PySide2.QtGui import     ( QIcon,
                                QPixmap,
                                QKeySequence,
                                QColor, QFont)
from PySide2.QtWidgets import ( QAction,
                                QGroupBox,
                                QHBoxLayout,
                                QLabel,
                                QToolBar,
                                QVBoxLayout,
                                QWidget,
                                QSplitter,
                                QSizePolicy,
                                QAbstractItemView,
                                QPushButton,
                                QFrame)

from deaduction.dui.utils               import   clear_layout
from deaduction.dui.elements            import (ActionButton,
                                                ProveUseModeSetter,
                                                ActionButtonsLine,
                                                ActionButtonsGroup,
                                                ActionButtonsLyt,
                                                StatementsTreeWidget,
                                                StatementsTreeWidgetItem,
                                                MathObjectWidget,
                                                MathObjectWidgetItem,
                                                TargetWidget,
                                                DeaductionStatusBar)
from deaduction.dui.primitives          import (deaduction_fonts,
                                                DeaductionTutorialDialog)

from deaduction.pylib.coursedata        import   Exercise
from deaduction.pylib.proof_state       import   Goal
import deaduction.pylib.config.vars      as      cvars
import deaduction.pylib.utils.filesystem as      fs

# from deaduction.pylib.text.tooltips import button_symbol

log = logging.getLogger(__name__)

global _


class ExerciseCentralWidget(QWidget):
    """
    Main / central / biggest widget in the exercise window. Self is to
    be instantiated as the central widget of d∃∀duction, more
    specifically as ExerciseMainWindow.centralWidget(). This widgets
    contains many crucial children widgets:
        - the target widget (self.target_wgt);
        - the 'context area' widgets:
            - the objects widget (self.objects_wgt) for math. objects
              (e.g. f:X->Y a function);
            - the properties widget (self.props_wgt) for math.
              properties (e.g. f is continuous);
        - the 'action area' widgets:
            - the action buttons,
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

    :attribute logic_btns ActionButtonsLine: Logic buttons available
        for this exercise.
    :attribute objects_wgt MathObjectWidget: Widget for context
        objects (e.g. f:X->Y a function).
    :attribute proof_btns ActionButtonsLine: Proof buttons
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

    context_title = _('Context (objects and properties) #{history_nb}')

    def __init__(self, exercise: Exercise):
        """
        Init self with an instance of the class Exercise. See
        self.__doc__.

        :param exercise: The instance of the Exercise class representing
            the exercise to be solved by the user.
        """
        super().__init__()
        self.exercise = exercise
        self.history_nb = 0

        # ───────────── Init layouts and boxes ───────────── #

        self.__main_lyt = QVBoxLayout()
        self.__context_lyt = QVBoxLayout()
        self.__context_actions_lyt = QHBoxLayout()
        self.__actions_lyt = QVBoxLayout()
        self.__action_btns_lyt = None  # init by init_action_layout

        # self.__action_btns_lyt.setContentsMargins(0, 0, 0, 0)
        self.__actions_gb = None
        context_title = self.context_title.format(history_nb=self.history_nb)
        self.__context_gb = QGroupBox(context_title)

        # ──────────────── Init Context area ─────────────── #
        self.objects_wgt = MathObjectWidget()
        self.props_wgt = MathObjectWidget()
        self.props_wgt.is_props_wdg = True
        for wdg in (self.objects_wgt, self.props_wgt):
            wdg.context_selection = self.context_selection
            wdg.clear_context_selection = self.clear_context_selection

        self.splitter = True
        self.__context_splitter = QSplitter(Qt.Vertical)
        self.init_context_layout()
        self.__context_gb.setLayout(self.__context_lyt)
        self.__context_gb.setSizePolicy(QSizePolicy.Maximum,
                                        QSizePolicy.Preferred)

        # ──────────────── Init Actions area ─────────────── #
        # Action buttons
        # ActionButton.from_name = dict()
        self.__prove_btns = ActionButtonsLine(exercise.available_logic_prove)
        self.__use_btns = ActionButtonsLine(exercise.available_logic_use)
        self.__logic_1_btns = ActionButtonsLine(exercise.available_logic_1)
        self.__logic_2_btns = ActionButtonsLine(exercise.available_logic_2)
        self.__compute_btns = ActionButtonsLine(exercise.available_compute)
        self.__magic_proof_btns = ActionButtonsLine(exercise.available_magic +
                                                    exercise.available_proof)

        # !! Somehow, this does not work for self.__prove_buttons if called
        # after these are set into ths GroupBox in switch mode, so I put it
        # here:

        self.init_action_btns_layout()

        # Statements
        statements           = exercise.available_statements
        outline              = exercise.course.outline
        self.statements_tree = StatementsTreeWidget(statements, outline)
        # The following prevents statements from begin nearly invisible
        # when there are few ActionButtons (so action_btns_lyt is narrow)
        if statements:
            self.statements_tree.setMinimumWidth(300)
        StatementsTreeWidgetItem.from_name = dict()
        self.set_actions_gb()
        self.__actions_gb.setSizePolicy(QSizePolicy.Minimum,
                                        QSizePolicy.Preferred)

        # ─────── Init goal (Context area and target) ────── #
        MathObjectWidgetItem.from_math_object = dict()
        self.target_wgt = TargetWidget()
        self.current_goal = None

        # Fonts
        self.deaduction_fonts = deaduction_fonts
        self.set_font()

        # ───────────── Put widgets in layouts ───────────── #
        # Context-action lyt #
        self.__vertical_splitter = QSplitter(Qt.Horizontal)
        self.__vertical_splitter.setChildrenCollapsible(False)
        self.__vertical_splitter.setSizePolicy(QSizePolicy.Expanding,
                                               QSizePolicy.Expanding)
        self.__vertical_splitter.addWidget(self.__context_gb)
        self.__vertical_splitter.addWidget(self.__actions_gb)
        self.__vertical_splitter.setStretchFactor(0, 3)
        self.__vertical_splitter.setStretchFactor(1, 1)
        self.__context_actions_lyt.addWidget(self.__vertical_splitter)

        # Set main layout
        self.organise_main_layout()  # Decide which one is on top
        self.setLayout(self.__main_lyt)


        # Drag and drop
        self.set_drag_and_drop_config()

    def init_context_layout(self):
        if self.splitter:
            self.__context_splitter.addWidget(self.objects_wgt)
            self.__context_splitter.addWidget(self.props_wgt)
            self.__context_splitter.setChildrenCollapsible(False)
            self.__context_lyt.addWidget(self.__context_splitter)
        else:
            self.__context_lyt.addWidget(self.objects_wgt)
            self.__context_lyt.addWidget(self.props_wgt)

        self.__context_gb.setTitle(_('Context (objects and properties)'))

    def splitter_state(self):
        return self.__vertical_splitter.saveState()

    def set_splitter_state(self, state):
        self.__vertical_splitter.restoreState(state)

    def set_switch_mode(self, to_prove=True):
        return self.__action_btns_lyt.set_switch_mode(to_prove)

    @property
    def switch_mode(self) -> str:
        """
        Return either 'prove' or 'use' or None.
        """
        return self.__action_btns_lyt.switch_mode

    def init_action_btns_layout(self):
        """
        This method populates self.__action_btns_lyt. The basic bricks are
        ActionButtonsWidgets, which are lines of ActionButtons. There are two
        cases:
        - In the simplest case, we just populate directly with
        ActionButtonsWidgets.
        - The more complicated case is when one or two buttons lines are
        prove or use lines. Then the layout is split into two QGroupBoxes,
        the first one will contain the prove/use buttons lines, maybe with a
        switcher, and the second one contains the other buttons.
        """

        # (1) Remove ActionButtonWidgets from layout
        if self.__action_btns_lyt:
            for action_buttons_widget in self.__action_buttons_lines:
                self.__action_btns_lyt.removeWidget(action_buttons_widget)

        # exercise = self.exercise
        mode = cvars.get('logic.button_use_or_prove_mode')

        # if exercise.prove_use_mode_set_by_exercise():
        #     dpu = False
        #     prove_wdg = None
        #     use_wdg = None
        #     other_wdgs = []
        if mode == 'display_unified':
            dpu = False
            prove_wdg = None
            use_wdg = None
            other_wdgs = [self.__logic_1_btns,
                          self.__logic_2_btns,
                          self.__magic_proof_btns]
        else:  # mode == "display_both" or "display_switch"
            # dpu = True
            prove_wdg = self.__prove_btns
            use_wdg = self.__use_btns
            other_wdgs = [self.__logic_2_btns,
                          self.__magic_proof_btns]

        switcher = (mode == 'display_switch')

        # List of (title, [ActionButtonsLine]):
        groups = [(_('Prove:'), [prove_wdg]),
                  (_('Use:'), [use_wdg]),
                  (None, other_wdgs),
                  (_('Compute (experimental):'), [self.__compute_btns])
                  ]
        self.__action_btns_lyt = ActionButtonsLyt(groups)
                                                  # display_prove_use=dpu,
                                                  # switcher=switcher)

        self.__action_btns_lyt.setSpacing(2)

    def set_actions_gb(self):
        action_title = _('Actions (logical rules and statements)')
        new_actions_gb = QGroupBox(action_title)

        # Insert btns and statements in layout
        self.__actions_lyt         = QVBoxLayout()

        self.__actions_lyt.setSpacing(10)
        # print(f"margins {self.__actions_lyt.contentsMargins()}")
        mode = cvars.get('logic.button_use_or_prove_mode')
        # self.__actions_lyt.setContentsMargins(0,
        #                                       0 if mode == "display_unified" else -2,
        #                                       0, 0)
        self.__actions_lyt.addLayout(self.__action_btns_lyt)
        self.__actions_lyt.addWidget(self.statements_tree)
        # Expand statements but not buttons:
        self.__actions_lyt.setStretch(0, 0)  # Buttons
        self.__actions_lyt.setStretch(1, 10)  # Statements

        new_actions_gb.setLayout(self.__actions_lyt)
        new_actions_gb.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        # self.__context_actions_lyt.addWidget(new_actions_gb)
        self.__actions_gb = new_actions_gb

    def set_drag_and_drop_config(self):
        # (1) Drags statements:
        if cvars.get('functionality.drag_statements_to_context', True):
            self.statements_tree.setDragEnabled(True)
            self.statements_tree.setDragDropMode(QAbstractItemView.DragOnly)
        else:
            self.statements_tree.setDragEnabled(False)
        # Drops in statements:
        if cvars.get('functionality.drag_context_to_statements', True):
            self.statements_tree.setAcceptDrops(True)
            self.statements_tree.setDragDropMode(QAbstractItemView.DropOnly)
        else:
            self.statements_tree.setAcceptDrops(False)
        if cvars.get('functionality.drag_context_to_statements', True) \
                and cvars.get('functionality.drag_statements_to_context', True):
            self.statements_tree.setDragDropMode(QAbstractItemView.DragDrop)

        # (2) Set context drag and drop:
        if cvars.get('functionality.drag_context_to_statements', True) \
                or cvars.get('functionality.drag_and_drop_in_context', True):
            self.props_wgt.setDragEnabled(True)
        else:
            self.props_wgt.setDragEnabled(False)

        if cvars.get('functionality.drag_and_drop_in_context', True):
            self.props_wgt.setDragDropMode(QAbstractItemView.DragDrop)
            self.objects_wgt.setDragDropMode(QAbstractItemView.DragDrop)
            self.objects_wgt.setDragEnabled(True)
        elif cvars.get('functionality.drag_context_to_statements', True) \
                and cvars.get('functionality.drag_statements_to_context', True):
            self.props_wgt.setDragDropMode(QAbstractItemView.DragDrop)
            self.objects_wgt.setDragEnabled(False)
            self.objects_wgt.setDragDropMode(QAbstractItemView.NoDragDrop)
        elif cvars.get('functionality.drag_context_to_statements', True):
            self.props_wgt.setDragDropMode(QAbstractItemView.DragOnly)
            self.objects_wgt.setDragEnabled(False)
            self.objects_wgt.setDragDropMode(QAbstractItemView.NoDragDrop)
        elif cvars.get('functionality.drag_statements_to_context', True):
            self.props_wgt.setDragDropMode(QAbstractItemView.DropOnly)
            self.objects_wgt.setDragEnabled(False)
            self.objects_wgt.setDragDropMode(QAbstractItemView.NoDragDrop)
        else:
            self.objects_wgt.setDragEnabled(False)
            self.objects_wgt.setDragDropMode(QAbstractItemView.NoDragDrop)
            self.props_wgt.setDragDropMode(QAbstractItemView.NoDragDrop)

##############################
# Methods called by __init__ #
##############################

    @property
    def __action_buttons_lines(self) -> [ActionButtonsLine]:
        return [self.__prove_btns,
                self.__use_btns,
                self.__logic_1_btns,
                self.__logic_2_btns,
                self.__magic_proof_btns,
                self.__compute_btns]

    @property
    def action_buttons(self,
                       include_hidden_buttons=True) -> [ActionButton]:
        if self.__action_btns_lyt:
            buttons = self.__action_btns_lyt.buttons
            sub_buttons = ((button.sub_buttons for button in buttons)
                           if include_hidden_buttons else [])
            return list(sum(sub_buttons, buttons))
        else:
            return []

    def show_action_button(self, name):
        for button in self.action_buttons:
            if button.name == name or button.symbol == name:
                button.show()

    def hide_action_button(self, name):
        for button in self.action_buttons:
            if button.name == name or button.symbol == name:
                button.hide()

    def show_complete_button(self, yes=True):
        if yes:
            self.show_action_button(name='complete')
        else:
            self.hide_action_button(name='complete')

    @property
    def action_button_names(self) -> [str]:
        return [btn.name for btn in self.action_buttons]

    def set_font_for_action_buttons(self):
        symbol_size = deaduction_fonts.symbol_button_font_size
        for btn in self.action_buttons:
            btn.update()
            if btn.is_symbol():
                btn.setFont(deaduction_fonts.math_fonts(size=symbol_size))

    def set_font(self):
        """
        OBSOLETE doc:
        Set the font size for some sub-widgets.
        Button font sizes are set in the widgets methods.
        Target font size is set in TargetWidget.
        ActionButtonsLine max-height is set so that they keep their nice
        appearance on Mac, whatever the font size.
        """

        # List styles: Modify color for selected objects
        background_color = cvars.get("display.color_for_selection", "limegreen")
        color = QColor(background_color)
        for wdg in [self.props_wgt, self.objects_wgt,
                    self.target_wgt.target_label]:
            # FIXME: this does not work HERE for self.statements_tree
            palette = wdg.palette()
            palette.setBrush(palette.Normal, palette.Highlight, color)
            palette.setBrush(palette.Inactive, palette.Highlight, color)
            wdg.setPalette(palette)

        self.set_font_for_action_buttons()

    def organise_main_layout(self):
        """
        Organize main layout, namely putting target on top or not according
        to self.target_display_on_top. To be called at __init__ and after
        preferences update.
        """
        if self.__main_lyt.count() > 0:
            if self.target_display_on_top and \
                    self.__main_lyt.indexOf(self.target_wgt) != 0:
                # context_actions_lyt = self.__main_lyt.itemAt(0)
                self.__main_lyt.removeItem(self.__context_actions_lyt)
                self.__main_lyt.addLayout(self.__context_actions_lyt)
            elif not self.target_display_on_top and \
                    self.__main_lyt.indexOf(self.target_wgt) == 0:
                self.__main_lyt.removeWidget(self.target_wgt)
                self.__main_lyt.addWidget(self.target_wgt)
        else:
            if self.target_display_on_top:
                self.__main_lyt.addWidget(self.target_wgt)
                self.__main_lyt.addLayout(self.__context_actions_lyt)
            else:
                self.__main_lyt.addLayout(self.__context_actions_lyt)
                self.__main_lyt.addWidget(self.target_wgt)

    def update_statements_tooltips(self, check_availability=False):
        if self.statements_tree:
            self.statements_tree.update_tooltips(
                check_availability=check_availability)

    def update(self):
        """
        Update
            - titles everywhere,
            - text and tooltips of all buttons.
        """
        self.__actions_gb.setTitle(_('Actions and statements (transform '
                                     'context and target)'))
        self.__context_gb.setTitle(_('Context (objects and properties)'))

        # for buttons in (self.logic_btns, self.proof_btns, self.magic_btns):
        #     buttons.update()
        for btn in self.action_buttons:
            btn.update()

    ##############
    # Properties #
    ##############
    @property
    def target_display_on_top(self):
        return cvars.get('display.target_display_on_top', True)

    ###########
    # Methods #
    ###########
    def action_button(self, symbol) -> ActionButton:
        """
        Return the ActionButton whose symbol is symbol.
        :param symbol: Symbol of som ActionButton, which is displayed on the
        button.
        """
        return ActionButton.from_symbol.get(symbol)

    def freeze(self, yes=True):
        """
        Freeze interface (inactive widgets, gray appearance, etc) if
        yes:
            - disable objects and properties;
            - disable all buttons;
        unfreeze it otherwise.

        :param yes: See above.
        """

        to_freeze = [# self.__context_gb,
                     self.objects_wgt,
                     self.props_wgt,
                     self.__actions_gb]
        for widget in to_freeze:
            if widget:
                widget.setEnabled(not yes)

    def __show__shaded_tutorial(self):
        cname = "dialogs.used_in_proof_intro"
        cname_exo = cname + "_exo"
        if cvars.get(cname) and cvars.get(cname_exo, True):
            text = _("<div>The properties that have already been used in the "
                     "proof are shaded in the context.<br> </div>"
                     "<div>Note that this does <b>not</b> prevent you from "
                     "using them again!<br> </div>")
            calc_intro_box = DeaductionTutorialDialog(config_name=cname,
                                                      text=text)
            cvars.set(cname_exo, False)  # Enough for this exercise
            calc_intro_box.exec()

    def __show__bold_tutorial(self):
        cname = "dialogs.new_object_intro"
        cname_exo = cname + "_exo"
        if cvars.get(cname) and cvars.get(cname_exo, True):
            text = _("<div>The new objects or properties appear in bold in the "
                     "context.<br> </div>")
            calc_intro_box = DeaductionTutorialDialog(config_name=cname,
                                                      text=text)
            cvars.set(cname_exo, False)  # Enough for this exercise
            calc_intro_box.exec()

    def update_goal(self, new_goal: Goal,
                    pending_goals,
                    history_nb=None):
        """
        Change goal widgets (self.objects_wgts, self.props_wgt and
        self.target_wgt) to new widgets, corresponding to new_goal.

        @param new_goal: The goal to update self to.
        @param pending_goals: The list of remaining goals. For the moment we
        just display the nb of pending goals.
        @param history_nb: History nb; if history_nb = 0 then no bold for new
        objects.
        """

        # # FIXME!!!!!
        # self.calculator = CalculatorController(context=new_goal.context_objects)
        # self.calculator.show()
        #

        if history_nb is not None:
            self.history_nb = history_nb
            title = self.context_title.format(history_nb=self.history_nb)
            self.__context_gb.setTitle(title)

        statements_scroll = self.statements_tree.verticalScrollBar().value()

        new_target     = new_goal.target
        new_objects = new_goal.context_objects
        new_props = new_goal.context_props
        self.objects_wgt.use_boldface = bool(self.history_nb)
        self.props_wgt.use_boldface = bool(self.history_nb)
        self.objects_wgt.set_math_objects(new_objects)
        self.props_wgt.set_math_objects(new_props)

        pgn = len(pending_goals)
        self.target_wgt.replace_target(new_target)
        self.target_wgt.set_pending_goals_counter(pgn)

        self.current_goal = new_goal

        self.statements_tree.verticalScrollBar().setValue(statements_scroll)

        if new_goal.new_objects:
            self.objects_wgt.scrollToBottom()
        if new_goal.new_props:
            self.props_wgt.scrollToBottom()

        if new_goal.contains_used_in_proof:
            self.__show__shaded_tutorial()
        if new_goal.contains_new_or_modified_context:
            self.__show__bold_tutorial()

    def context_selection(self):
        return self.objects_wgt.selected_items() \
               + self.props_wgt.selected_items()

    def clear_context_selection(self):
        self.objects_wgt.clearSelection()
        self.props_wgt.clearSelection()


class ExerciseStatusBar(DeaductionStatusBar):

    def __init__(self, parent):
        super().__init__(parent)
        # Waiting timer
        self.waiting_timer.timeout.connect(self.add_point)

    @property
    def display_success_msgs(self):
        return cvars.get('display.display_success_messages', True)

    def manage_msgs(self, proof_step):
        """
        Display a message in the status bar. Three kinds of messages are
        considered: new goal, error or success.
        - New goal msgs are normal msgs, i.e. they will remain in the status
        bar unless they are hidden temporarily by a temporary msg.
        e.g. "First case: we assume a in A".
        - success and error msgs are temporary msgs.
        """

        self.stop_timer()

        # self.enable_msgs()
        if proof_step.is_error():
            tmp_msg = proof_step.error_msg
        else:
            tmp_msg = proof_step.success_msg

        if proof_step.is_error():
            # log.debug("StatusBar: " + tmp_msg)
            self.show_error_msg(tmp_msg)
        elif proof_step.success_msg and self.display_success_msgs:
            # log.debug("StatusBar: " + tmp_msg)
            self.show_success_msg(tmp_msg)
        else:
            self.hide_icon()
            tmp_msg = ""

        # Show proof msg if any:
        if tmp_msg:
            duration = self.pending_msg_time_interval
            self.timer.setInterval(duration)
            # self.timer.singleShot(duration, self.show_pending_msgs)
            self.timer.start()
        else:  # Show immediately
            self.show_pending_msgs()


class CalculatorStatusBar(DeaductionStatusBar):
    pass


class ExerciseToolBar(QToolBar):
    """
    A toolbar for tools concerning current exercise.
    """

    def __init__(self):
        super().__init__(_('Toolbar'))
        icons_base_dir = cvars.get("icons.path")
        icons_dir = fs.path_helper(icons_base_dir)
        self.rewind = QAction(
                QIcon(str((icons_dir / 'goback-begining.png').resolve())),
                _('Jump to beginning of proof'), self)
        self.undo_action = QAction(
                QIcon(str((icons_dir / 'undo_action.png').resolve())),
                _('Undo action'), self)
        self.redo_action = QAction(
                QIcon(str((icons_dir / 'redo_action.png').resolve())),
                _('Redo action'), self)
        self.go_to_end = QAction(
                QIcon(str((icons_dir / 'go-end-96.png').resolve())),
                _('Jump to end of proof'), self)

        self.toggle_proof_outline_action = QAction(
                QIcon(str((icons_dir / 'proof_outline.png').resolve())),
            _('Toggle proof outline'), self)

        self.toggle_proof_tree = QAction(
                QIcon(str((icons_dir / 'proof_tree.png').resolve())),
            _('Toggle proof global view'), self)

        self.toggle_lean_editor_action = QAction(
                QIcon(str((icons_dir / 'lean_editor.png').resolve())),
                _('Toggle L∃∀N'), self)

        self.toggle_help_action = QAction(
                QIcon(str((icons_dir / 'help-48.png').resolve())),
                _('Toggle help window'), self)

        self.addAction(self.rewind)
        self.addAction(self.undo_action)
        self.addAction(self.redo_action)
        self.addAction(self.go_to_end)
        self.addSeparator()
        self.addAction(self.toggle_proof_outline_action)
        self.addAction(self.toggle_proof_tree)
        self.addAction(self.toggle_lean_editor_action)
        self.addAction(self.toggle_help_action)
        self.undo_action.setShortcut(QKeySequence.Undo)
        self.redo_action.setShortcut(QKeySequence.Redo)

        self.toggle_proof_outline_action.setCheckable(True)
        self.toggle_proof_tree.setCheckable(True)
        self.toggle_lean_editor_action.setCheckable(True)
        self.toggle_help_action.setCheckable(True)

    def update(self):
        self.rewind.setText(_('Jump to beginning of proof'))
        self.undo_action.setText(_('Undo action'))
        self.redo_action.setText(_('Redo action'))
        self.go_to_end.setText(_('Jump to end of proof'))
        self.toggle_lean_editor_action.setText(_('Toggle L∃∀N'))
        self.toggle_proof_outline_action.setText(_('Toggle proof outline'))
        self.toggle_proof_tree.setText(_("Toggle proof tree"))
        self.toggle_help_action.setText(_('Toggle help window'))


class GlobalToolbar(QToolBar):
    def __init__(self):
        super().__init__(_('Toolbar'))
        icons_base_dir = cvars.get("icons.path")
        icons_dir = fs.path_helper(icons_base_dir)
        self.stop = QAction(
                QIcon(str((icons_dir / 'icons8-stop-sign-48').resolve())),
                _('Stop me from thinking!'), self)
        # self.stop.setShortcut(QKeySequence(QKeySequence.Cancel))

        self.settings_action = QAction(
                QIcon(str((icons_dir / 'settings').resolve())),
                _('Settings'), self)
        self.settings_action.setShortcut(QKeySequence(
                                                QKeySequence.Preferences))
        self.change_exercise_action = QAction(
                QIcon(str((icons_dir / 'change_exercise.png').resolve())),
                _('Change exercise'), self)
        self.save_history_action = QAction(
            QIcon(str((icons_dir / 'icons8-save-96.png').resolve())),
            _("Save proof"), self)

        self.addAction(self.stop)
        self.addAction(self.settings_action)
        self.addAction(self.save_history_action)
        self.save_history_action.setShortcut(QKeySequence.Save)
        self.addAction(self.change_exercise_action)
        self.setLayoutDirection(Qt.RightToLeft)

        # self.change_exercise_action.setCheckable(True)
        # self.settings_action.setCheckable(True)

    def update(self):
        self.change_exercise_action.setText(_('Change exercise'))
        self.settings_action.setText(_("Settings"))
        self.stop.setText(_('Stop me from thinking!'))
        self.save_history_action.setText(_("Save proof"))


