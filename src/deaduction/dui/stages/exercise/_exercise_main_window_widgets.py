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
                                QStatusBar,
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
                                                ActionButtonsWidget,
                                                ActionButtonsLyt,
                                                StatementsTreeWidget,
                                                StatementsTreeWidgetItem,
                                                MathObjectWidget,
                                                MathObjectWidgetItem,
                                                TargetWidget)
from deaduction.dui.primitives          import deaduction_fonts

from deaduction.pylib.coursedata        import   Exercise
from deaduction.pylib.proof_state       import   Goal
import deaduction.pylib.config.vars      as      cvars
import deaduction.pylib.utils.filesystem as      fs

from deaduction.pylib.text.tooltips import button_symbol

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
        self.__action_btns_lyt     = None  # init by init_action_layout

        # self.__action_btns_lyt.setContentsMargins(0, 0, 0, 0)
        action_title = _('Actions (logical rules and statements)')
        context_title = _('Context (objects and properties)')
        self.__actions_gb = QGroupBox(action_title)
        self.__context_gb = QGroupBox(context_title)

        # ──────────────── Init Actions area ─────────────── #
        ActionButton.from_name = dict()
        self.__action_btns_wdgs = []  # Used to freeze buttons

        statements           = exercise.available_statements
        outline              = exercise.course.outline
        self.statements_tree = StatementsTreeWidget(statements, outline)
        StatementsTreeWidgetItem.from_name = dict()

        # ─────── Init goal (Context area and target) ────── #
        MathObjectWidgetItem.from_math_object = dict()
        self.target_wgt   = TargetWidget()
        self.current_goal = None
        self.objects_wgt  = MathObjectWidget()
        self.props_wgt    = MathObjectWidget()
        self.props_wgt.is_props_wdg = True
        for wdg in (self.objects_wgt, self.props_wgt):
            wdg.context_selection = self.context_selection
            wdg.clear_context_selection = self.clear_context_selection

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

        # Fonts
        self.deaduction_fonts = deaduction_fonts
        self.set_font()

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

    @property
    def set_switch_mode(self):
        return self.__action_btns_lyt.set_switch_mode

    @property
    def switch_mode(self) -> str:
        """
        Return either 'prove' or 'use' or None.
        """
        return self.__action_btns_lyt.switch_mode

    def init_action_layout(self):
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

        This method is called by __init__, but also when updating after the
        settings are changed from one case to the other one.
        """
        exercise = self.exercise

        # ───────────── Action buttons ───────────── #
        mode = cvars.get('logic.button_use_or_prove_mode')

        if exercise.prove_use_mode_set_by_exercise():
            # TODO!!
            dpu = False
            prove_line = []
            use_line = []
            other_lines = []
            virtual_lines = []
        elif mode == 'display_unified':
            dpu = False
            prove_line = []
            use_line = []
            other_lines = [exercise.available_logic_1]
            virtual_lines = [exercise.available_logic_prove,
                             exercise.available_logic_use]
        else:  # mode == "display_both" or "display_switch"
            dpu = True
            prove_line = exercise.available_logic_prove
            use_line = exercise.available_logic_use
            other_lines = []
            virtual_lines = [exercise.available_logic_1]

        other_lines += [exercise.available_logic_2,
                        exercise.available_magic + exercise.available_proof]

        switcher = (mode == 'display_switch')

        # TODO:
        #  update ecw in new_settings in case mode changed
        #  fonts!? bad font for prove
        #  set by user
        #  adapt help msgs
        #  automatic actions: (OK) define buttons and connect signals even if
        #   buttons are not displayed (self.actions_buttons)
        #   --> Ca clignote pas !!!
        #  (OK?) and_use et and_prove non discriminants
        #  (OK?) exists_use avec 'x' --> mauvais msg d'erreur
        #  option and/or unified
        prove_wdg = ActionButtonsWidget(prove_line)
        use_wdg = ActionButtonsWidget(use_line)
        other_line_wdgs = [ActionButtonsWidget(line) for line in other_lines]
        virtual_line_wdgs = [ActionButtonsWidget(line) for line in virtual_lines]
        self.__action_btns_lyt = ActionButtonsLyt(other_line_wdgs,
                                                  prove_wdg,
                                                  use_wdg,
                                                  display_prove_use=dpu,
                                                  switcher=switcher)

        self.__action_btns_wdgs = ([prove_wdg, use_wdg]
                                   + other_line_wdgs
                                   + virtual_line_wdgs)

        # ───────────── Statements ───────────── #
        statements = exercise.available_statements
        outline = exercise.course.outline
        self.statements_tree = StatementsTreeWidget(statements, outline)

        # Put action buttons and statement tree in lyt
        self.__actions_lyt.addLayout(self.__action_btns_lyt)
        self.__action_btns_lyt.setSpacing(2)
        self.__actions_lyt.addWidget(self.statements_tree)

        # Expand statements but not buttons:
        self.__actions_lyt.setStretch(0, 0)
        self.__actions_lyt.setStretch(1, 10)

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

    def set_font(self):
        """
        OBSOLETE doc:
        Set the font size for some sub-widgets.
        Button font sizes are set in the widgets methods.
        Target font size is set in TargetWidget.
        ActionButtonsWidget max-height is set so that they keep their nice
        appearance on Mac, whatever the font size.
        """

        # OBSOLETE: this is done in font_config
        # # Sizes #
        # main_size = self.deaduction_fonts.main_font_size
        # tooltip_size = self.deaduction_fonts.tooltips_font_size
        # symbol_size = self.deaduction_fonts.symbol_button_font_size
        # style = f'QTreeWidget {{font-size: {main_size}}}' \
        #         f'QListView {{font-size: {main_size}}}' \
        #         f'QToolTip {{font-size: {tooltip_size};}}' \
        #         # f'ActionButton {{max-height: 30px; ' \
        #         # f'font-size: {symbol_size} }}'
        # self.setStyleSheet(style)

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

        # Modify font for symbol buttons
        symbol_size = self.deaduction_fonts.symbol_button_font_size
        for btns_wdg in self.__action_btns_wdgs:
            if btns_wdg:
                for btn in btns_wdg.buttons:
                    btn.update()
                    if btn.is_symbol():
                        btn.setFont(deaduction_fonts.math_fonts(size=symbol_size))
                        # btn.setFont(deaduction_fonts.math_fonts(size=20))

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

        # for buttons in (self.logic_btns, self.proof_btns, self.magic_btns):
        #     buttons.update()
        for btn in self.actions_buttons:
            btn.update()

    ##############
    # Properties #
    ##############
    @property
    def target_display_on_top(self):
        return cvars.get('display.target_display_on_top', True)

    @property
    def actions_buttons(self) -> [ActionButton]:
        """
        A list of all logic buttons and proof
        buttons (instances of the class ActionButton).
        """
        btns = []
        for line in self.__action_btns_wdgs:
            btns.extend(line.buttons)
        return btns
        # return self.logic_btns.buttons \
        #         + self.proof_btns.buttons \
        #         + self.magic_btns.buttons

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

        to_freeze = [self.objects_wgt,
                     self.props_wgt,
                     # self.logic_btns,
                     # self.proof_btns,
                     # self.magic_btns,
                     self.statements_tree]
                     # self.prove_use_mode_setter]
        to_freeze += self.__action_btns_wdgs
        for widget in to_freeze:
            if widget:
                widget.setEnabled(not yes)

    def update_goal(self, new_goal: Goal,
                    pending_goals):
        """
        Change goal widgets (self.objects_wgts, self.props_wgt and
        self.target_wgt) to new widgets, corresponding to new_goal.

        @param new_goal: The goal to update self to.
        @param pending_goals: The list of remaining goals. For the moment we
        just display the nb of pending goals.
        """

        statements_scroll = self.statements_tree.verticalScrollBar().value()

        new_target     = new_goal.target
        new_objects = new_goal.context_objects
        new_props = new_goal.context_props
        self.objects_wgt.set_math_objects(new_objects)
        self.props_wgt.set_math_objects(new_props)

        pgn = len(pending_goals)
        self.target_wgt.replace_target(new_target)
        self.target_wgt.set_pending_goals_counter(pgn)

        self.current_goal = new_goal
        # self.set_font()

        self.statements_tree.verticalScrollBar().setValue(statements_scroll)

    def context_selection(self):
        return self.objects_wgt.selected_items() \
               + self.props_wgt.selected_items()

    def clear_context_selection(self):
        self.objects_wgt.clearSelection()
        self.props_wgt.clearSelection()


class ExerciseStatusBar(QStatusBar):
    """
    A pending msg can be displayed after a timeout.
    This is used to display msgs about the structure of the proof
    (e.g. "Proof of first implication").
    Pending msgs are stored in the LILO list self.pending_msgs.
    A pending msg may be cancelled: if a user action happens before timeout,
    the msg is replaced by "". Note that a new pending msgs may be added by
    the action, with a new timeout ; this is why the cancelled msgs is
    erased but a blank msg stays in the list.
    """

    def __init__(self, parent):
        super().__init__(parent)

        # Waiting timer
        self.waiting_timer = QTimer(self)
        self.waiting_timer.timeout.connect(self.add_point)

        # Pending msgs
        self.timer = QTimer(self)
        # self.pending_msgs = []
        self.proof_msg: callable = None  # This will be set from outside

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

        # Help button
        self.help_button = QPushButton(_("Help"))

        # Insert icon and message
        self.insertWidget(0, self.iconWidget)
        self.insertWidget(1, self.messageWidget)

        self.addWidget(self.help_button)
        self.help_button.hide()
        self.show_success_icon()  # Trick: the status bar adapts its height
        self.hide_icon()

    @property
    def txt(self):
        return self.messageWidget.text()

    @property
    def display_success_msgs(self):
        return cvars.get('display.display_success_messages', True)

    @Slot()
    def add_point(self):
        """
        Add a point (.) at the end of the msg.
        """
        msg = self.messageWidget.text()
        self.messageWidget.setText(msg + '.')

    def display_thinking_bar(self):
        self.set_message(_("    Thinking"))
        self.messageWidget.setStyleSheet("font-style: italic")
        self.waiting_timer.start(1000)

    def display_initializing_bar(self):
        self.set_message(_("    Initializing"))
        self.messageWidget.setStyleSheet("font-style: italic")
        self.waiting_timer.start(500)

    def stop_thinking(self):
        self.waiting_timer.stop()
        self.messageWidget.setStyleSheet("font-style: normal")

    def show_pending_msgs(self):
        """
        This method is called by the timer, when there is a new_goal msg to
        display on top of the usual success/error msgs.
        """

        proof_msg = self.proof_msg()
        if proof_msg:
            self.show_normal_msg(proof_msg)

    def show_error_icon(self):
        self.iconWidget.setPixmap(self.error_pixmap)
        self.iconWidget.show()

    def show_success_icon(self):
        self.iconWidget.setPixmap(self.success_pixmap)
        self.iconWidget.show()

    def hide_icon(self):
        self.iconWidget.hide()

    def set_message(self, msg: str):
        self.stop_thinking()
        self.messageWidget.setText(msg)
        return

    def erase(self):
        self.set_message("")
        self.hide_icon()

    @Slot()
    def show_normal_msg(self, msg):
        # log.debug("StatusBar: show " + msg)
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

        if self.timer.isSingleShot():
            self.timer.stop()
        # self.enable_msgs()
        if proof_step.is_error():
            tmp_msg = proof_step.error_msg
        else:
            tmp_msg = proof_step.success_msg

        if proof_step.is_error():
            # log.debug("StatusBar: " + tmp_msg)
            self.show_error_icon()
            self.set_message(tmp_msg)
        elif proof_step.success_msg and self.display_success_msgs:
            # log.debug("StatusBar: " + tmp_msg)
            self.show_success_icon()
            self.set_message(tmp_msg)
        else:
            self.hide_icon()
            tmp_msg = ""

        # Show proof msg if any:
        if tmp_msg:
            self.timer.singleShot(3000, self.show_pending_msgs)
        else:  # Show immediately
            self.show_pending_msgs()

    def show_tmp_msg(self, msg: str, duration=3000):
        self.set_message(msg)
        self.timer.singleShot(3000, self.erase)
        self.timer.singleShot(3000, self.show_pending_msgs)


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
        self.toggle_help_action.setText(_('Toggle help window'))


class GlobalToolbar(QToolBar):
    def __init__(self):
        super().__init__(_('Toolbar'))
        icons_base_dir = cvars.get("icons.path")
        icons_dir = fs.path_helper(icons_base_dir)
        self.stop = QAction(
                QIcon(str((icons_dir / 'icons8-stop-sign-48').resolve())),
                _('Stop me from thinking!'), self)
        self.stop.setShortcut(QKeySequence(QKeySequence.Cancel))

        self.settings_action = QAction(
                QIcon(str((icons_dir / 'settings').resolve())),
                _('Settings'), self)
        self.settings_action.setShortcut(QKeySequence(
                                                QKeySequence.Preferences))
        self.change_exercise_action = QAction(
                QIcon(str((icons_dir / 'change_exercise.png').resolve())),
                _('Change exercise'), self)

        self.addAction(self.stop)
        self.addAction(self.settings_action)
        self.addAction(self.change_exercise_action)
        self.setLayoutDirection(Qt.RightToLeft)

        # self.change_exercise_action.setCheckable(True)
        # self.settings_action.setCheckable(True)

    def update(self):
        self.change_exercise_action.setText(_('Change exercise'))
        self.settings_action.setText(_("Settings"))
        self.cancel_server.setText(_("Stop computations"))


