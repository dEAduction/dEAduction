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

from PySide2.QtGui import     ( QIcon,
                                QPixmap )
from PySide2.QtWidgets import ( QAction,
                                QGroupBox,
                                QHBoxLayout,
                                QLabel,
                                QStatusBar,
                                QToolBar,
                                QVBoxLayout,
                                QWidget)

from deaduction.dui.utils               import   replace_widget_layout
from deaduction.dui.elements            import ( ActionButton,
                                                 ActionButtonsWidget,
                                                 StatementsTreeWidget,
                                                 MathObjectWidget,
                                                 TargetWidget)
from deaduction.pylib.config.i18n       import   _
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

        actions_gb = QGroupBox(_('Actions and statements (transform context '
                                 'and target)'))
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

        target_display_on_top = cvars.get('display.target_display_on_top',
                                          True)
        if target_display_on_top:
            self.__main_lyt.addWidget(self.target_wgt)
            self.__main_lyt.addLayout(context_actions_lyt)
        else:
            self.__main_lyt.addLayout(context_actions_lyt)
            self.__main_lyt.addWidget(self.target_wgt)

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
        replace_widget_layout(self.__context_lyt,
                              self.objects_wgt, new_objects_wgt)
        replace_widget_layout(self.__context_lyt,
                              self.props_wgt, new_props_wgt)
        replace_widget_layout(self.__main_lyt,
                              self.target_wgt, new_target_wgt, True)

        # Set the attributes to the new values
        self.objects_wgt  = new_objects_wgt
        self.props_wgt    = new_props_wgt
        self.target_wgt   = new_target_wgt
        self.current_goal = new_goal


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

        # Verbose mode
        self.display_success_messages = cvars.get(
            'display.display_success_messages', True)

    def show_error_icon(self):
        self.iconWidget.setPixmap(self.error_pixmap)
        self.iconWidget.show()

    def show_success_icon(self):
        self.iconWidget.setPixmap(self.success_pixmap)
        self.iconWidget.show()

    def hide_icon(self):
        self.iconWidget.hide()

    def set_message(self, message: str):
        self.messageWidget.setText(message)

    def erase(self):
        self.set_message("")
        self.hide_icon()

    def display_message(self, proof_step):
        """
        Display a message in the status bar. Two kinds of messages are
        considered: error or success.
        """

        #log.debug(f"Display msg: "
        #          f"{proof_step.error_msg, proof_step.success_msg}")
        if proof_step.is_error():
            message = proof_step.error_msg
        else:
            message = proof_step.success_msg
        # Capitalize first char but do not un-capitalize the remaining
        if message:
            message = message[0].capitalize() + message[1:]

        if proof_step.is_error():
            self.show_error_icon()
            self.set_message(message)
        elif proof_step.success_msg and self.display_success_messages:
            self.show_success_icon()
            self.set_message(message)
        else:
            self.hide_icon()


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

        self.toggle_lean_editor_action = QAction(
                QIcon(str((icons_dir / 'lean_editor.png').resolve())),
                _('Toggle L∃∀N'), self)

        self.change_exercise_action = QAction(
                QIcon(str((icons_dir / 'change_exercise.png').resolve())),
                _('Change exercise'), self)


        self.addAction(self.rewind)
        self.addAction(self.undo_action)
        self.addAction(self.redo_action)
        self.addAction(self.toggle_lean_editor_action)
        self.addSeparator()
        self.addAction(self.change_exercise_action)
