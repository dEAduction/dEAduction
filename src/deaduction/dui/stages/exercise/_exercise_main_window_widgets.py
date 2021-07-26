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

from functools import partial
from PySide2.QtCore import    ( Signal,
                                Slot,
                                QTimer,
                                Qt)

from PySide2.QtGui import     ( QIcon,
                                QPixmap )
from PySide2.QtWidgets import ( QAction,
                                QGroupBox,
                                QHBoxLayout,
                                QLabel,
                                QStatusBar,
                                QToolBar,
                                QVBoxLayout,
                                QWidget,
                                QSplitter,
                                QSizePolicy)

from deaduction.dui.utils               import   replace_widget_layout
from deaduction.dui.elements            import ( ActionButton,
                                                 ActionButtonsWidget,
                                                 StatementsTreeWidget,
                                                 MathObjectWidget,
                                                 TargetWidget)
from deaduction.pylib.actions           import   action_apply
from deaduction.pylib.coursedata        import   Exercise
from deaduction.pylib.mathobj           import   Goal
import deaduction.pylib.config.vars      as      cvars
import deaduction.pylib.utils.filesystem as      fs

log = logging.getLogger(__name__)


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
        self.exercise = exercise

        # ───────────── Init layouts and boxes ───────────── #
        # I wish none of these were class atributes, but we need at
        # least self.__main_lyt and self.__context_lyt in the method
        # self.update_goal.

        self.__main_lyt     = QVBoxLayout()
        self.__context_lyt  = QVBoxLayout()
        self.__context_actions_lyt = QHBoxLayout()
        self.__actions_lyt         = QVBoxLayout()
        self.__action_btns_lyt     = QVBoxLayout()

        self.__action_btns_lyt.setContentsMargins(0, 0, 0, 0)
        self.__action_btns_lyt.setSpacing(0)

        self.__actions_gb = QGroupBox(_('Actions and statements (transform '
                                      'context and target)'))
        self.__context_gb = QGroupBox(_('Context (objects and properties)'))
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

        statements           = exercise.available_statements
        outline              = exercise.course.outline
        self.statements_tree = StatementsTreeWidget(statements, outline)

        # ─────── Init goal (Context area and target) ────── #
        self.current_goal = None
        self.objects_wgt  = MathObjectWidget()
        self.props_wgt    = MathObjectWidget()
        self.target_wgt   = TargetWidget()

        # ───────────── Put widgets in layouts ───────────── #

        # Actions
        self.init_action_layout()
        self.__actions_gb.setLayout(self.__actions_lyt)

        # Context
        self.splitter = True
        self.__context_splitter = QSplitter(Qt.Vertical)
        self.init_context_layout()
        self.__context_gb.setLayout(self.__context_lyt)

        # Size policies:
        #       - Context should be able to expand at will, since properties
        #       arbitrarily long
        #       - Actions should be fixed size, determined by the
        #       number of buttons
        self.__context_gb.setSizePolicy(QSizePolicy.Expanding,
                                        QSizePolicy.Preferred)
        self.__actions_gb.setSizePolicy(QSizePolicy.Fixed,
                                        QSizePolicy.Preferred)

        # https://i.kym-cdn.com/photos/images/original/001/561/446/27d.jpg

        self.__context_actions_lyt.addWidget(self.__context_gb)
        self.__context_actions_lyt.addWidget(self.__actions_gb)

        self.organise_main_layout()  # Decide which one is on top
        self.setLayout(self.__main_lyt)

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

    def init_action_layout(self):
        exercise = self.exercise

        # ───────────── Action buttons ───────────── #

        self.logic_btns = ActionButtonsWidget(exercise.available_logic)
        self.proof_btns = ActionButtonsWidget(exercise.available_proof)
        self.magic_btns = ActionButtonsWidget(exercise.available_magic)

        # Search for ActionButton corresponding to action_apply
        # (which will be called by double-click):
        apply_buttons = [button for button in self.proof_btns.buttons
                         if button.action.run == action_apply]
        if apply_buttons:
            self.action_apply_button = apply_buttons[0]

        self.__action_btns_lyt.addWidget(self.logic_btns)
        self.__action_btns_lyt.addWidget(self.proof_btns)
        if exercise.available_magic:
            self.__action_btns_lyt.addWidget(self.magic_btns)

        # ───────────── Statements ───────────── #
        statements = exercise.available_statements
        outline = exercise.course.outline
        self.statements_tree = StatementsTreeWidget(statements, outline)

        # Put action buttons and statement tree in lyt
        self.__actions_lyt.addLayout(self.__action_btns_lyt)
        self.__actions_lyt.addWidget(self.statements_tree)

##############################
# Methods called by __init__ #
##############################
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
            elif  not self.target_display_on_top and \
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

    def update(self):
        """
        Update
            - titles everywhere,
            - text and tooltips of all buttons.
        """

        self.__actions_gb.setTitle(_('Actions and statements (transform '
                                     'context and target)'))
        self.__context_gb.setTitle(_('Context (objects and properties)'))

        for buttons in (self.logic_btns, self.proof_btns, self.magic_btns):
            buttons.update()

    ##############
    # Properties #
    ##############
    @property
    def target_display_on_top(self):
        return cvars.get('display.target_display_on_top', True)

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
    def action_button(self, symbol) -> ActionButton:
        """
        Return the ActionButton whose symbol is symbol.
        :param symbol: Symbol of som ActionButton, which is displayed on the
        button.
        """
        buttons = [button for button in self.actions_buttons if
                   button.has_symbol(symbol)]
        if buttons:
            return buttons[0]
        else:
            return None

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

    def update_goal(self, new_goal: Goal,
                    current_goal_number: int,
                    total_goals_counter: int):
        """
        Change goal widgets (self.objects_wgts, self.props_wgt and
        self.target_wgt) to new widgets, corresponding to new_goal.

        :param new_goal: The goal to update self to.
        studied
        :param current_goal_number: n° of goal under study
        :param total_goals_counter: total number of goals so far
        """
        statements_scroll = self.statements_tree.verticalScrollBar().value()

        # Init context (objects and properties). Get them as two list of
        # (MathObject, str), the str being the tag of the prop. or obj.
        new_context    = new_goal.tag_and_split_propositions_objects()
        new_target     = new_goal.target
        new_target_tag = '='  # new_target.future_tags[1]
        new_objects    = new_context[0]
        new_props      = new_context[1]

        new_objects_wgt = MathObjectWidget(new_objects)
        new_props_wgt   = MathObjectWidget(new_props)
        goal_count = f'  {current_goal_number} / {total_goals_counter}'
        new_target_wgt  = TargetWidget(new_target, new_target_tag, goal_count)

        # Replace in the layouts
        if self.splitter:
            new_splitter = QSplitter(Qt.Vertical)
            new_splitter.addWidget(new_objects_wgt)
            new_splitter.addWidget(new_props_wgt)
            new_splitter.setChildrenCollapsible(False)
            replace_widget_layout(self.__context_lyt,
                                  self.__context_splitter, new_splitter)
            self.__context_splitter = new_splitter
            # Unfortunately, the following does not always work
            # log.debug("Splitter widgets:")
            # log.debug(self.__context_splitter.count())
            # self.__context_splitter.replaceWidget(0, new_objects_wgt)
            # self.__context_splitter.replaceWidget(1, new_props_wgt)
        else:
            replace_widget_layout(self.__context_lyt,
                                  self.objects_wgt, new_objects_wgt)
            replace_widget_layout(self.__context_lyt,
                                  self.props_wgt, new_props_wgt)

        replace_widget_layout(self.__main_lyt,
                              self.target_wgt, new_target_wgt, True)

        # Set the attributes to the new values
        # self.__context_splitter = new_context_wgt
        self.objects_wgt  = new_objects_wgt
        self.props_wgt    = new_props_wgt
        self.target_wgt   = new_target_wgt
        self.current_goal = new_goal

        # FIXME:
        #  Modify main layout if needed (e;G. target_on_top has changed)
        # self.organise_main_layout()

        self.statements_tree.verticalScrollBar().setValue(statements_scroll)


class ExerciseStatusBar(QStatusBar):
    # TODO: Docstring me and all methods

    def __init__(self, parent):
        super().__init__(parent)

        # Icon
        self.iconWidget = QLabel(self)
        icons_base_dir = cvars.get("icons.path")
        error_icon_path = fs.path_helper(icons_base_dir) / 'cancel.png'
        success_icon_path = fs.path_helper(icons_base_dir) / 'checked.png'
        self.error_pixmap = QPixmap(str(error_icon_path.resolve()))
        self.success_pixmap = QPixmap(str(success_icon_path.resolve()))
        self.iconWidget.setScaledContents(True)
        self.iconWidget.setMaximumSize(self.height(), self.height())

        # Message
        self.messageWidget = QLabel("", self)

        # Insert icon and message
        self.insertWidget(0, self.iconWidget)
        self.insertWidget(1, self.messageWidget)
        self.show_success_icon()  # Trick: the status bar adapts its height
        self.hide_icon()

    def show_error_icon(self):
        self.iconWidget.setPixmap(self.error_pixmap)
        self.iconWidget.show()

    def show_success_icon(self):
        self.iconWidget.setPixmap(self.success_pixmap)
        self.iconWidget.show()

    def hide_icon(self):
        self.iconWidget.hide()

    def set_message(self, msg: str):
        self.messageWidget.setText(msg)

    def erase(self):
        self.set_message("")
        self.hide_icon()

    @Slot()
    def show_normal_msg(self, msg):
        log.debug("StatusBar: show " + msg)
        self.hide_icon()
        self.set_message(msg)

    def manage_msgs(self, proof_step):
        """
        Display a message in the status bar. Three kinds of messages are
        considered: new goal, error or success.
        - New goal msgs are normal msgs, i.e. they will remain in the status
        bar unless they are hidden temporarily by a temporary msg.
        e.g. "First case: we assume a in A".
        - success and error msgs are temporary msgs.
        """

        if proof_step.is_error():
            tmp_msg = proof_step.error_msg
        else:
            tmp_msg = proof_step.success_msg
        # Capitalize first char but do not un-capitalize the remaining
        if tmp_msg:  # Fixme: remove and capitalize msgs correctly!
            tmp_msg = tmp_msg[0].capitalize() + tmp_msg[1:]

        if proof_step.is_error():
            log.debug("StatusBar: " + tmp_msg)
            self.show_error_icon()
            self.set_message(tmp_msg)
        elif proof_step.success_msg and self.display_success_msgs:
            log.debug("StatusBar: " + tmp_msg)
            self.show_success_icon()
            self.set_message(tmp_msg)
        else:
            self.hide_icon()
            tmp_msg = ""

        if proof_step.new_goals:
            new_goal = proof_step.new_goals[-1]
            if new_goal:
                # Set QTimer for normal msg
                if tmp_msg:
                    log.debug("StatusBar timer " + new_goal.msg)
                    timer = QTimer(self)
                    func = partial(self.show_normal_msg, new_goal.msg)
                    timer.singleShot(3000, func)  # 3000 = 3sec
                else:  # Show immediately
                    self.show_normal_msg(new_goal.msg)

    @property
    def display_success_msgs(self):
        return cvars.get('display.display_success_messages', True)


class ExerciseToolBar(QToolBar):
    # TODO: Docstring me and all methods

    def __init__(self):
        super().__init__(_('Toolbar'))
        icons_base_dir = cvars.get("icons.path")
        icons_dir = fs.path_helper(icons_base_dir)
        self.rewind = QAction(
                QIcon(str((icons_dir / 'goback-begining.png').resolve())),
                _('Go back to beginning of proof'), self)
        self.undo_action = QAction(
                QIcon(str((icons_dir / 'undo_action.png').resolve())),
                _('Undo action'), self)
        self.redo_action = QAction(
                QIcon(str((icons_dir / 'redo_action.png').resolve())),
                _('Redo action'), self)

        self.toggle_proof_outline_action = QAction(
                QIcon(str((icons_dir / 'proof_outline.png').resolve())),
            _('Toggle proof outline'), self)

        self.toggle_lean_editor_action = QAction(
                QIcon(str((icons_dir / 'lean_editor.png').resolve())),
                _('Toggle L∃∀N'), self)

        self.change_exercise_action = QAction(
                QIcon(str((icons_dir / 'change_exercise.png').resolve())),
                _('Change exercise'), self)

        self.addAction(self.rewind)
        self.addAction(self.undo_action)
        self.addAction(self.redo_action)
        self.addAction(self.toggle_proof_outline_action)
        self.addAction(self.toggle_lean_editor_action)
        self.addSeparator()
        self.addSeparator()
        self.addAction(self.change_exercise_action)
        # self.setLayoutDirection(Qt.RightToLeft)

    def update(self):
        self.rewind.setText(_('Go back to beginning of proof'))
        self.undo_action.setText(_('Undo action'))
        self.redo_action.setText(_('Redo action'))
        self.toggle_lean_editor_action.setText(_('Toggle L∃∀N'))
        self.change_exercise_action.setText(_('Change exercise'))
        self.toggle_proof_outline_action.setText(_('Toggle proof outline'))
