"""
#########################################################
# actions_widgets_classes.py : exercise actions widgets #
#########################################################

    Provide widgets classes for an exercise's actions area, that is the
    two rows of action buttons (logic buttons and proof techniques
    buttons) and the so-called statements tree : course definitions,
    theorems and exercises used as theorems are displayed in a tree
    whose structure is that of the course. Those widgets will be
    instantiated in ExerciseCentralWidget, which itself will be
    instantiated as an attribute of ExerciseMainWindow. Provided
    classes:
        - ActionButton;
        - ActionButtonsLine;
        - StatementsTreeWidgetNode;
        - StatementsTreeWidgetItem;
        - StatementsTreeWidget.

Author(s)      : Kryzar <antoine@hugounet.com>
Maintainers(s) : Kryzar <antoine@hugounet.com>
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

import logging
from functools import partial
from typing import Dict, Optional

from pyside2uic.Compiler.qtproxies import QtCore, QtGui
from trio import sleep

from PySide2.QtGui     import ( QBrush,
                                QColor,
                                QIcon,
                                QCursor,
                                QPainter,
                                QBrush,
                                QPen)
from PySide2.QtCore    import ( Signal,
                                Slot,
                                Qt,
                                QModelIndex, QMimeData,
                                QTimer,
                                QRect,
                                QPoint)
from PySide2.QtWidgets import (QHBoxLayout,
                               QVBoxLayout,
                               QPushButton,
                               QWidget,
                               QAbstractItemView,
                               QLabel,
                               QGroupBox,
                               QStackedLayout,
                               QMenu, QAction, QToolButton)

from PySide2.QtWidgets import ( QTreeWidget,
                                QTreeWidgetItem,
                                QToolTip,
                                QSizePolicy)

from deaduction.dui.primitives import RichTextToolButton, deaduction_fonts
from deaduction.pylib.text        import ( button_symbol,
                                           button_tool_tip)
import deaduction.pylib.config.dirs as cdirs

from deaduction.pylib.actions     import   Action
from deaduction.pylib.coursedata  import ( Definition,
                                           Exercise,
                                           Statement,
                                           Theorem)
from deaduction.dui.utils         import   set_selectable

import deaduction.pylib.config.vars as cvars
import deaduction.pylib.utils.filesystem as fs

log = logging.getLogger(__name__)
global _

#################################
# Action button widgets classes #
#################################

# Classes for the two rows of buttons (e.g. ∀ button) in the Actions
# area of the exercise window. Each button is coded as an instance of
# the class ActionButton and each row essentially is a container of
# instances of ActionButton coded as an instance of ActionButtonsLine.


class ActionButton(QToolButton):
    """
    Class for so-called 'action buttons' (e.g. '∀' button). Each
    instance of this class is associated to an instance of the class
    Action (self.action). This instance contains
    all information required by L∃∀N. Furthermore, each
    such instance also contains all required cosmetic information
    for the graphical interface, that is a symbol and a caption.
    Therefore, all one needs to instantiate ActionButton is an instance
    of the class Action.

    Let exercisemainwindow be the instance of the class ExerciseMainWindow
    of which self is a child. When self is clicked on:
        1. the signal self.__statement_triggered is emitted;
        2. this signal is received in exercisemainwindow.server_task;
        3. exercisemainwindow.__server_call_action is called and from
           there on the current goal, optional current selection (user
           selected objects and properties) and self are pre-processed.
           If everything is ok, everything is sent to L∃∀N. Otherwise,
           additional info may be asked to the user, such as missing
           parameters.
    Behavior is analogous to StatementsTreeWidgetItem's.

    :attribute action Action: The instance of the Action class self was
        instantiated with.
    :attribute action_triggered (Signal(ActionButton)): A Signal with
        self as an argument, emitted when self is clicked on.
    """

    def __init__(self, action: Action, sub_buttons=None,
                 in_demo_or_use_line=False):
        """
        Init self with an instance of the class Action. Set text,
        tooltip and keep the given action as an attribute. When self is
        clicked on, emit the signal self.action_triggered.

        :param action: The instance of the class Action one wants
            self to be associated with.
        :param sub_buttons: Other ActionButton which will be simulated in
        self.menu.
        """

        super().__init__()
        self.setMinimumSize(70, 30)
        # self.set_text_mode(True)
        self.action = action
        self.sub_buttons = sub_buttons

        # Modify button default color
        if cvars.get('others.os') == "linux":

            background_color = cvars.get("display.color_for_selection",
                                         "limegreen")
            self.set_color(background_color)

        self.in_demo_or_use_line = in_demo_or_use_line
        self.update()  # set symbol and tool tip
        self.clicked.connect(self.emit_action)
        # Modify arrow appearance when over a button
        self.setCursor(QCursor(Qt.PointingHandCursor))

        self.set_menu()

    def set_menu(self):
        """
        Set a pop-up menu if self has sub_actions.
        """

        if not self.sub_buttons:
            return

        menu = QMenu(self)

        for button in self.sub_buttons:
            menu_action = QAction(button.action.name, self)
            menu_action.triggered.connect(button.emit_action)
            menu.addAction(menu_action)

        self.setMenu(menu)
        self.setPopupMode(QToolButton.MenuButtonPopup)
        menu.setToolTipsVisible(True)

    def set_color(self, color):
        palette = self.palette()
        highlight_color = QColor(color)
        palette.setBrush(palette.Normal, palette.Button, highlight_color)
        palette.setBrush(palette.Inactive, palette.Button, highlight_color)
        self.setPalette(palette)

    def __symbol_from_name(self, name):
        symbol = button_symbol(name)
        if self.in_demo_or_use_line:
            # Remove ugly prefix, 'use_' or 'prove_'
            if symbol.startswith('use'):
                symbol = symbol[4:]
            elif symbol.startswith('prove'):
                symbol = symbol[6:]
        symbol = _(symbol)  # Translate, finally!
        return  symbol

    @staticmethod
    def __tooltip_from_name(name):
        tool_tip = button_tool_tip(name)
        if isinstance(tool_tip, str):
            tooltip = _(tool_tip)
        elif isinstance(tool_tip, list):
            pretty_list = []
            for msg in tool_tip:
                if msg.endswith(':'):
                    msg = _("Button") + " " + _(msg[:-1]) + _(":")
                else:
                    msg = "• " + _(msg)
                pretty_list.append(msg)
            tooltip = '\n'.join(pretty_list)
        else:
            tooltip = ""

        return tooltip

    def update(self):
        """
        Set or update text and tooltips in button, using module pylib.text.
        NB: translation is done here.
        """

        self.setText(self.__symbol_from_name(self.name))
        self.setToolTip(self.__tooltip_from_name(self.name))

        if self.menu():
            for button, menu_action in zip(self.sub_buttons,
                                           self.menu().actions()):
                menu_action.setText(self.__symbol_from_name(button.name))
                menu_action.setToolTip(self.__tooltip_from_name(button.name))

    @Slot()
    def emit_action(self):
        """
        Emit the signal self.action_triggered with self as an argument.
        This slot is connected to ActionButton.clicked signal in
        self.__init__.
        """
        self.action_triggered.emit(self)

    @property
    def symbol(self):
        """
        Actual text displayed on self (can be changed by usr).
        """
        return self.text()
        # return self.action.symbol

    def is_symbol(self):
        """
        Should be true iff self is a math symbol, e.g. '⇒' or '='.
        The test is only that length = 1...
        The other option could be to provide a list.
        """
        test = len(self.symbol) < 4  # , not self.symbol.isascii())
        return test

    @property
    def name(self):
        """
        (Immutable) name of the corresponding action.
        One of  ['forall', 'exists', 'implies', 'and', 'or',
                 'not', 'iff', 'equal', 'map',
                 'prove_forall', 'use_forall', ...]
        """
        return self.action.name

    def has_symbol(self, symbol) -> bool:
        """
        Test if symbol is the symbol of (the action associated to) self.
        """
        # TODO: obsolete (?) startswith --> ends_with ?
        return self.action.symbol.startswith(symbol) \
            or self.action.symbol.startswith(symbol.replace('_', ' ')) \
            or _(self.action.symbol).startswith(_(symbol)) \
            or _(self.action.symbol).startswith(_(symbol.replace('_', ' ')))

    async def simulate(self, duration=0.3, winkle_nb=2):
        """
        This method simulate user pushing self. It is asynchrone since we
        must wait a small duration before unchecking button, so that the
        checking is visible. This is called when redoing.
        :param duration: total duration
        """
        duration = duration/(3*winkle_nb)
        for n in range(winkle_nb):
            self.setCheckable(True)
            self.setChecked(True)
            await sleep(2*duration)
            self.setChecked(False)
            self.setCheckable(False)
            await sleep(duration)

    async def simulate_sub_button(self, sub_button,
                                  duration=0.3, winkle_nb=2,
                                  trigger=True) -> bool:
        """
        Simulate usr click on the corresponding item in self.menu().
        """
        try:
            idx = self.sub_buttons.index(sub_button)
        except ValueError:
            return False

        menu_action = self.menu().actions()[idx]
        pos = self.mapToGlobal(QPoint(0, self.frameGeometry().height()))
        self.menu().popup(pos)
        duration = duration/(3*winkle_nb)
        for n in range(winkle_nb):
            self.menu().setActiveAction(menu_action)
            await sleep(2*duration)
            self.menu().setActiveAction(None)
            await sleep(duration)
        self.menu().close()
        if trigger:
            menu_action.trigger()
        return True

# We wish to have an ActionButton class attribute called
# action_triggered and defined as Signal(ActionButton). At first, one
# may define it in ActionButton.__init__. However, doing this will raise
# an exception because in ActionButton.__init__, the class ActionButton
# is not *yet* defined. The workaround is to define this class attribute
# outside of the class definition, as followed.
ActionButton.action_triggered = Signal(ActionButton)


class Switch(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        # self.setMinimumWidth(66)
        # self.setMinimumHeight(22)

    def paintEvent(self, event):
        # label = _("DEMO") if self.isChecked() else _("USE")
        bg_color = Qt.green
        label = ""
        radius = 5
        width = 20
        factor = 1.5
        center = self.rect().center()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(center)
        painter.setBrush(QColor(0, 0, 0))

        pen = QPen(Qt.black)
        pen.setWidth(2)
        painter.setPen(pen)

        painter.drawRoundedRect(QRect(-width, -radius, 2*width,
                                            2*radius),
                                radius, radius)
        painter.setBrush(QBrush(bg_color))
        # sw_rect = QRect(-radius, -radius, width + radius, 2*radius)
        btn_radius = int(radius*factor)
        sw_rect = QRect(-btn_radius, -btn_radius, 2*btn_radius,
                        2*btn_radius)
        if not self.isChecked():
            sw_rect.moveLeft(-width)
        else:
            sw_rect.moveRight(width)
        painter.drawEllipse(sw_rect)
        # painter.drawText(sw_rect, Qt.AlignCenter, label)


class ProveUseModeSetter(QWidget):
    """
    A switch (QPush button displaying two positions) to switch between proof
    mode and use mode.
    """
    clicked = Signal()

    def __init__(self):
        super().__init__()
        self.switch = Switch()
        self.switch.setChecked(True)
        demo_lbl = QLabel(_("Prove mode"))
        use_lbl = QLabel(_("Use mode"))

        lyt = QHBoxLayout()
        lyt.setContentsMargins(0, 0, 0, 0)

        lyt.addStretch()
        lyt.addWidget(use_lbl)
        lyt.addWidget(self.switch)
        lyt.addWidget(demo_lbl)
        self.setLayout(lyt)

        self.switch.clicked.connect(self.clicked)

    @property
    def switch_mode(self):
        if self.switch.isChecked():
            return "prove"
        else:
            return "use"

    def click(self):
        self.switch.setChecked(not self.switch.isChecked())
        self.clicked.emit()


class ActionButtonsLine(QWidget):
    """
    A container class to create and display an ordered row of instances
    of the class Action as buttons (instances of the class
    ActionButton). Each element of this list inits an instance of the
    class ActionButton; this instance is set to be a child of self and
    is kept as an attribute in self.buttons.

    :param buttons [ActionButton]: The list of instances of the class
        ActionButton created and displayed in self.__init__. This
        attribute makes accessing them painless.
    self.demo_line is True iff all buttons are demo buttons.
    """

    init = False

    @classmethod
    def set_lbl_size(cls):
        if cls.init:  # Size already set
            return

        cls.init = True
        # Determine fixed width
        demo_lbl = QLabel(_('Prove:'))
        use_lbl = QLabel(_('Use:'))
        demo_lbl.show()
        use_lbl.show()
        cls.__lbl_width = max(demo_lbl.width(), use_lbl.width())
        cls.__lbl_height = demo_lbl.height()
        # print(lbl_height, lbl_width)
        demo_lbl.deleteLater()
        use_lbl.deleteLater()

    def __init__(self, actions: [Action]):
        """
        Init self with an ordered list of instances of the class Action.
        :param actions: The list of instances of the class Action one
            wants to create buttons from.
        demo_line is True iff all buttons are 'prove' buttons. In this case,
        a QLabel display 'Prove :'. Likewise for use_line.

        The bool show_label allows display of a label 'Prove:' or 'Use:'
        (obsolete).
        """

        super().__init__()
        self.actions = self.__organize_actions(actions)

        self.set_lbl_size()

        self.demo_line = all((action.name.startswith('prove_')
                              for action in actions))
        self.use_line = all((action.name.startswith('use_')
                             for action in actions))
        demo_or_use_line = self.demo_line or self.use_line

        self.buttons = []

        # (1) Populate h_layout with ActionButtons
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        for action, subactions in self.actions:
            sub_buttons = [ActionButton(sub_action,
                                        in_demo_or_use_line=demo_or_use_line)
                           for sub_action in subactions]

            action_button = ActionButton(action,
                                         sub_buttons=sub_buttons,
                                         in_demo_or_use_line=demo_or_use_line)
            h_layout.addWidget(action_button)
            self.buttons.append(action_button)

        h_layout.addStretch()

        self.setLayout(h_layout)

        sp = self.sizePolicy()
        sp.setRetainSizeWhenHidden(True)
        self.setSizePolicy(sp)

    # @property
    # def demo_line(self):
    #     return all(button.action.name.startswith('prove_')
    #                for button in self.buttons)

    @staticmethod
    def __organize_actions(actions):
        """
        Put as sub-actions those actions whose name starts with the name of
        some other previous action in actions.
        e.g.
            action_prove_exists_joker
        is a sub-action of
            action_prove_exists.
        """

        organized_actions: [tuple] = []
        idx = 0
        while idx < len(actions):
            action = actions[idx]
            name = action.name
            sub_actions = []
            jdx = idx+1
            while jdx < len(actions):
                other_action = actions[jdx]
                if other_action.name.startswith(name):
                    sub_actions.append(other_action)
                    actions.pop(jdx)
                jdx += 1
            organized_actions.append((action, sub_actions))
            idx += 1

        return organized_actions

    def names(self):
        return [button.name for button in self.buttons]

    def button_from_name(self, name):
        for button in self.buttons:
            if button.name == name:
                return button


class ProveUseSwitcherButtonGroupBox(QGroupBox):
    """
    This class is a QGrouBox with two lines of buttons. If switcher is True
    then a button allow usr to switch between lines, otherwise both lines are
    displayed.
    """
    def __init__(self, prove_wdgs, use_wdgs, switcher=True):
        super().__init__()
        self.prove_wdgs = prove_wdgs
        self.use_wdgs = use_wdgs
        self.lyt = QVBoxLayout()
        self.prove_use_mode_setter = None
        # self.toggled.connect(self.hide)
        # self.recorded_height = 0

        if not switcher:  # Just the two buttons lines
            self.prove_use_mode_setter = None
            self.stacked_lyt = None
            self.lyt.addWidget(prove_wdgs)
            self.lyt.addWidget(use_wdgs)

        else:
            # Switcher
            self.prove_use_mode_setter = ProveUseModeSetter()
            self.prove_use_mode_setter.clicked.connect(
                self.update_switch)
            self.lyt.addWidget(self.prove_use_mode_setter)
            self.lyt.setAlignment(self.prove_use_mode_setter, Qt.AlignHCenter)

            # Stacked_lyt with prove and use wdgs
            self.stacked_lyt = QStackedLayout()
            self.stacked_lyt.addWidget(prove_wdgs)
            self.stacked_lyt.addWidget(use_wdgs)
            self.stacked_lyt.setCurrentIndex(0)
            self.lyt.addLayout(self.stacked_lyt)

        self.setLayout(self.lyt)
        self.update_switch()

    def update_switch(self):
        if self.prove_use_mode_setter:
            switch_mode = self.prove_use_mode_setter.switch_mode
            if switch_mode == "prove":
                self.stacked_lyt.setCurrentIndex(0)
            elif switch_mode == "use":
                self.stacked_lyt.setCurrentIndex(1)

    @property
    def switch_mode(self):
        if self.prove_use_mode_setter:
            return self.prove_use_mode_setter.switch_mode

    def set_switch_mode(self, to_prove=True):
        if self.prove_use_mode_setter:

            change = ((to_prove and self.switch_mode == "use")
                      or (not to_prove) and self.switch_mode == "prove")
            if change:
                self.prove_use_mode_setter.click()

    # def hide(self):
    #     if self.isChecked():
    #         self.setMaximumHeight(self.recorded_height)
    #         self.prove_wdgs.show()
    #         self.use_wdgs.show()
    #         self.setFlat(False)
    #     else:
    #         self.recorded_height = self.height()
    #         self.prove_wdgs.hide()
    #         self.use_wdgs.hide()
    #         self.setFlat(True)
    #         self.setMaximumHeight(20)
    #         # self.lyt.setMargin(0)
    #         # self.lyt.setContentsMargins(0,0,0,0)


class ActionButtonsGroup(QGroupBox):
    """
    This class is a QGroupbox with a title containing one or several
    ActionButtonLines.

    The title could be made clickable (e.g. a checkbox) to allow hide/show
    the box.
    """

    def __init__(self, title, action_button_lines: [ActionButtonsLine]):
        super().__init__()
        self.setTitle(title)
        self.lyt = QVBoxLayout()
        self.action_button_lines = action_button_lines
        self.buttons = []
        # self.no_button = True
        for abw in action_button_lines:
            if abw.buttons:
                self.buttons.extend(abw.buttons)
                # self.no_button = False
                self.lyt.addWidget(abw)

        self.setLayout(self.lyt)

    @property
    def no_button(self) -> bool:
        return not bool(self.buttons)

    # def button_from_name(self, name):
    #     for abl in self.action_button_lines:
    #         name = abl.button_from_name(name)
    #         if name:
    #             return name

    # def __init__(self, title, action_button_wdgs: [ActionButtonsLine]):
    #     super().__init__()
    #
    #     # 1 or 2 widgets
    #     self.title_wdg = QCheckBox(title) if title else None
    #     self.group_box = QGroupBox()
    #     self.gb_lyt = QVBoxLayout()
    #
    #     for abw in action_button_wdgs:
    #         self.gb_lyt.addWidget(abw)
    #     self.group_box.setLayout(self.gb_lyt)
    #
    #     self.lyt = QVBoxLayout()
    #     self.lyt.setContentsMargins(0,0,0,0)
    #     self.lyt.setMargin(0)
    #
    #     if self.title_wdg:
    #         self.title_wdg.setChecked(True)
    #         self.lyt.addWidget(self.title_wdg)
    #         self.title_wdg.stateChanged.connect(self.show_or_hide)
    #
    #     self.lyt.addWidget(self.group_box)
    #     self.setLayout(self.lyt)
    #
    # def show_or_hide(self):
    #     if not self.title_wdg:
    #         return
    #
    #     if self.title_wdg.isChecked():
    #         self.group_box.show()
    #
    #     else:
    #         self.group_box.hide()


class ActionButtonsLyt(QVBoxLayout):
    """
    This class provides a QVBoxLayout which contains all action buttons.
    The action buttons are first grouped by lines in ActionButtonsLines,
    and lines are grouped in a ActionButtonsGroup with a title:
    thus the entry data are of type [(str, [[Actions]])].

    Fixme, obsolete:
    There are two cases:
    - either prove_wdgs and use_wdgs are provided, then these are used to
    build a ProveUseSwitcherButtonGroupBox, and the other line wdgs are put
    in another QGroupBox;
    - or all the line wdgs are directly put into self.
    """

    def __init__(self, action_buttons_lines: [(str, [[ActionButtonsLine]])],
                 switcher=False):
        super().__init__()
        self.buttons = []
        for (title, group) in action_buttons_lines:
            group_box = ActionButtonsGroup(title, group)
            if not group_box.no_button:
                self.addWidget(group_box)
                self.buttons.extend(group_box.buttons)

    @classmethod
    def from_actions(cls, actions_lines: [(str, [[Action]])]):
        """
        The action buttons are first grouped by lines in ActionButtonsLines,
        and lines are grouped in a ActionButtonsGroup with a title:
        thus the entry data are of type [(str, [[Actions]])].
        """
        pass

    # # FIXME:
    # @classmethod
    # def obsolete(cls,
    #              other_line_wdgs: [ActionButtonsLine],
    #              prove_wdgs: ActionButtonsLine = None,
    #              use_wdgs: ActionButtonsLine = None,
    #              display_prove_use=False,
    #              switcher=True):
    #
    #     super().__init__()
    #
    #     # Try
    #     prove_wdgs = ActionButtonsGroup(_('Prove:'), [prove_wdgs])
    #     use_wdgs = ActionButtonsGroup(_('Use:'), [use_wdgs])
    #
    #     self.prove_use_box = None
    #     other_lyt = QVBoxLayout() if display_prove_use else self
    #
    #     # Populate other_lyt, in the simple case that's enough
    #     # first = True
    #     for wdg in other_line_wdgs:
    #         # if not first:
    #         #     pass
    #         #     # other_lyt.addSpacing(5)
    #         # else:
    #         #     first = False
    #         other_lyt.addWidget(wdg)
    #
    #     # In the complicated case, populate self with two QGroupBoxes
    #     if display_prove_use:
    #         self.prove_use_box = \
    #             ProveUseSwitcherButtonGroupBox(prove_wdgs, use_wdgs,
    #                                            switcher=switcher)
    #         # self.prove_use_box.setTitle('Prove or use')
    #         # self.prove_use_box.setCheckable(True)
    #         other_box = QGroupBox()
    #         other_box.setLayout(other_lyt)
    #
    #         self.prove_use_box.layout().setContentsMargins(5, 5, 5, 5)
    #         self.prove_use_box.layout().setSpacing(5)
    #         other_box.layout().setContentsMargins(5, 5, 5, 5)
    #         other_box.layout().setSpacing(5)
    #
    #         self.addWidget(self.prove_use_box)
    #         self.addWidget(other_box)

    def set_switch_mode(self, to_prove=True):
        if self.prove_use_box:
            return self.prove_use_box.set_switch_mode(to_prove)

    @property
    def switch_mode(self) -> str:
        if self.prove_use_box:
            return self.prove_use_box.switch_mode


##############################
# Statements widgets classes #
##############################

# Statements (definition, theorem, exercise (the class Exercise inherits
# from the class Theorem)) to be called while solving an exercise are
# coded in the following classes. In the graphical interface, those
# statements are represented in a tree (StatementsTreeWidget) preserving
# the course structure:
#   - each node (StatementsTreeWidgetNode) corresponds to a course
#     chapter/section/… (e.g. 'Topological spaces');
#   - each leaf (StatementsTreeWidgetItem) corresponds to a statement
#     (e.g. 'Bolzano-Weierstrass theorem').
# Even though StatementsTreeWidgetItem and StatementsTreeWidgetNode are
# not protected nor private, they should not be instantiated outside
# this module. The so-called 'statements tree' is automatically created
# by StatementsTreeWidget.__init__ given an ordered list of instances of
# the Statement class and it is this method which instantiates the items
# and nodes.


class StatementsTreeWidgetItem(QTreeWidgetItem):
    """
    This class is a tree item (inherits from QTreeWidgetItem) in charge
    of displaying an instance of the class (or child of) Statement.
    This instance contains all L∃∀N-understandable data and is kept as a
    class attribute (self.statement). Since such an instance itself
    contains cosmetic data (e.g. a title), one only needs an instance of
    the class Statement to instantiate a StatementsTreeWidgetItem.

    Let exercisemainwindow be the instance of the class ExerciseMainWindow
    of which self is a child. When self is is clicked on:
        1. the signal exercisemainwindow.__statement_triggered is
           emitted;
        2. this signal is received in exercisemainwindow.server_task;
        3. exercisemainwindow.__server_call_statement is called and the
           current goal, the user selection (obj. and prop.) and self
           are sent to L∃∀N for processing and eventually updating the
           interface to a new goal.
        3. exercisemainwindow.__server_call_statement is called and from
           there on the current goal, optional current selection (user
           selected objects and properties) and self are pre-processed.
           If everything is ok, everything is sent to L∃∀N.
    Behavior is analogous to ActionButton's.

    :attribute statement Statement: The instance of the class (or child
        of) Statement associated to self.
    """
    from_lean_name: dict = {}  # Statement.lean_name --> item
    # ! Must be updated to avoid pointing to deleted items !

    is_node = False

    def __init__(self, statement: Statement):
        """
        Init self with an instance of the class (or child of) Statement.

        :param statement: The instance of the class (or child) one wants
            to associate to self.
        """

        self.statement = statement
        self.parent = None  # Will be the QTreeWidget when inserted

        super().__init__(None, self.to_display())

        # Print second col. in gray
        self.setForeground(1, QBrush(QColor('gray')))
        # TODO: use mono font for lean name column (column 1)

        self.set_icon()

        self.from_lean_name[statement.lean_name] = self
        # if isinstance(statement, Exercise):
        #     print(fr"New TreeWdgItem for statement {statement.lean_name}")
        # Set tooltips: tooltips are set when item is put in the QTReeWidget
        # so that is_exercise property has a meaning
        # self.set_tooltip()

    def to_display(self) -> [str]:
        statement = self.statement
        # if StatementsTreeWidget.show_lean_name_for_statements:
        #     to_display = [statement.pretty_name, statement.lean_name]
        # else:
        #     to_display = [statement.pretty_name]
        # return to_display
        return [statement.pretty_name]

    def set_icon(self):
        # Print icon (D for definition, T for theorem, etc)
        icons_base_dir = cvars.get("icons.path")
        icons_type     = cvars.get("icons.letter_type")
        icons_dir = fs.path_helper(icons_base_dir) / icons_type
        statement = self.statement
        if isinstance(statement, Definition):
            path = icons_dir / 'd.png'
        elif isinstance(statement, Exercise):
            path = icons_dir / 'e.png'
        elif isinstance(statement, Theorem):
            path = icons_dir / 't.png'
        self.setIcon(0, QIcon(str(path.resolve())))

    @property
    def is_exercise(self):
        if self.parent:
            return self.parent.is_exercise_list

    def set_tooltip(self, only_ips=True, check_availability=False):
        """
        Set the math content of the statement as tooltip.
        If the flag only_ips is True, then no tooltips are shown if the
        initial proof states is not available. Otherwise the tooltip will
        show the Lean code content of the statement.
        """

        available = self.statement.initial_proof_state is not None
        if not available and check_availability:
            self.setDisabled(True)
            return
        else:
            self.setDisabled(False)

        text = self.statement.caption(is_exercise=self.is_exercise,
                                      only_ips=only_ips)
        if not text:
            return
        # Prevent wrap mode
        text = "<p style='white-space:pre'>" + text
        self.setToolTip(0, text)
        # These tooltips contain maths
        math_font_name = cvars.get('display.mathematics_font', 'Default')
        QToolTip.setFont(math_font_name)

    def has_pretty_name(self, pretty_name: str) -> bool:
        return self.statement.pretty_name == pretty_name

    async def simulate(self, duration=0.3, winkle_nb=2, expand=True):
        """
        This method simulate user selecting statement. It is asynchronous
        since we must wait a small duration so that the checking is visible.
        This is called when redoing.
        :param duration: total duration
        """
        color = cvars.get("display.color_for_selection", "LimeGreen")
        if expand:
            self.setExpanded(expand)
            self.treeWidget().scrollToItem(self)
        duration = duration /(3*winkle_nb)
        for n in range(winkle_nb):
            self.setBackground(0, QBrush(QColor(color)))
            await sleep(2*duration)
            self.setBackground(0, QBrush())
            await sleep(duration)

    @classmethod
    def from_statement(cls, statement):
        return cls.from_lean_name.get(statement.lean_name)

    @classmethod
    def from_end_of_lean_name(cls, name):
        for key in cls.from_lean_name:
            if key.endswith(name):
                return cls.from_lean_name[key]


class ChooseExerciseWidgetItem(StatementsTreeWidgetItem):

    def to_display(self) -> [str]:
        exercise = self.statement
        date = exercise.history_date()
        if date:
            nb_steps = len(exercise.refined_auto_steps)
            txt1 = _("saved on ") + date
            txt2 = f"({nb_steps} " + _("steps") + ")"
            # to_display = ['\t' + txt1 + '\t' + txt2]
            to_display = ['', txt1 + '\t' + txt2]
        else:
            to_display = [exercise.pretty_name]

        return to_display

    def set_icon(self):
        # icons_base_dir = cvars.get("icons.path")
        icons_base_dir = cdirs.icons
        icons_type     = cvars.get("icons.letter_type")
        icons_letter_dir = fs.path_helper(icons_base_dir) / icons_type

        exercise = self.statement
        assert isinstance(exercise, Exercise)

        if exercise.history_date():
            if exercise.is_solved_in_auto_test():
                path = icons_base_dir / 'checked.png'
            else:
                path = icons_base_dir / 'icons8-in-progress-96.png'
        elif exercise.is_solved_in_history_course():
            path = icons_base_dir / 'checked.png'
        elif exercise.has_versions_in_history_course():
            path = icons_base_dir / 'icons8-in-progress-96.png'
        else:
            path = icons_letter_dir / 'e.png'

        if path:
            self.setIcon(0, QIcon(str(path.resolve())))


class StatementsTreeWidgetNode(QTreeWidgetItem):
    """
    This class renders a hierarchical element of the course (e.g. a
    section) as an unclickable node in the so-called 'statements tree'.
    Statements (StatementsTreeWidgetItem) are children of those nodes.
    For example, given the section name 'Finite groups', self is a node
    with title 'Finite groups'.
    """

    is_node = True

    def __init__(self, title: str):
        """
        Init self with a title.

        :param title: The title to be displayed.
        """

        # QTreeWidget objects use columns to display titles. So if one
        # wants to display a unique title, it needs to be in a 1-element
        # list.
        super().__init__(None, [title])

        # Cosmetics
        self.setFlags(Qt.ItemIsEnabled)
        self.setExpanded(True)

    def add_child(self, child: QTreeWidgetItem):
        """
        Do not delete, used in StatementsTreeWidget._init_tree_branch! This
        method exists to uniformize notations in
        StatementsTreeWidget._init_tree_branch.

        :param child: Either an instance of StatementsTreeWidgetNode or
            StatementsTreeWidgetItem; to ba added as a child of self.
        """

        self.addChild(child)


class StatementsTreeWidget(QTreeWidget):
    """
    This class renders an ordered list of instances of the class
    Statement in a tree (inherits from QTreeWidget) presentation. The
    nodes correspond to hierarchical elements (e.g. chapter/sections/…)
    and the leaves to statements in this hierarchy. This class is
    instantiated with a list of instances of the class Statement and
    what we call an outline, which is just a Dict[str, str] (most of
    the time Exercise.outline attribute) of which keys are hierarchy
    levels (e.g. 'groups.finite_groups') and values are pretty names
    for display (e.g. 'Finite groups'). Furthermore, those instances
    contain all L∃∀N-understandable data. In order to instantiate
    StatementsTreeWidget, one only needs an instance of the class
    Statement and an outline (see above). 

    Here is an example of what the tree looks like given an ordered
    list of three statements with the following lean names:
        groups.first_definitions.definition.group,
        groups.first_definitions.theorem.Lagrange,
        rings.introduction.definition.ring;
    and the following outline:
        { 'groups': 'Groups',
          'groups.first_definitions': 'First definitions',
          'rings': 'Rings'
          'rings.introduction': 'Introduction'},
    we end up with the following tree:
        Groups (StatementsTreeWidgetNode)
        └─  First definitions (StatementsTreeWidgetNode)
            └─  (D) Definition (StatementsTreeWidgetItem)
            └─  (T) Lagrange's theorem (StatementsTreeWidgetItem)
        Rings (StatementsTreeWidgetNode)
        └─  Introduction (StatementsTreeWidgetNode)
            └─  (D) Definition (StatementsTreeWidgetItem)
    (D) and (T) represent icons which enable to distinguish definitions,
    theorems and exercises. Note that statements pretty names (which
    enable to display 'Lagranges's theorem instead of 'lagrange') are
    not in the outline, they are already coded in the instances of the
    class Statement themselves with the attribute pretty_name.
    """

    math_object_dropped = Signal(StatementsTreeWidgetItem)

    # TODO: Put this in self.__init__
    # Config
    depth_of_unfold_statements = \
                        cvars.get("display.depth_of_unfold_statements")

    # show_lean_name_for_statements = \
    #                 cvars.get("display.show_lean_name_for_statements")

    tooltips_font_size = cvars.get('display.tooltips_font_size', 10)

    # TODO: show lean names only when lean console is on
    # (even if show_lean_name_for_statements == TRUE)

    def _init_tree_branch(self, extg_tree, branch: [str],
                          expanded_flags: [bool],
                          statement: Statement, parent):
        """
        Add branch to extg_tree and StatementsTreeWidgetItem(statement)
        at the end of branch. This function is recursive.

        :param extg_tree: A tree implemented as a recursive
            dictionary, see self._init_tree.__doc__.
        :param branch: A tree branch (new or already existing), e.g.
            ['Chapter', 'Section', 'Sub-section']. Those are not
            instances of the class StatementsTreeWidgetNode!
        :param expanded_flags: list of booleans corresponding to branch,
        expanded_flags[n] = True if branch[n] must be expanded
        :param statement: The instance of the
            class Statement one wants to represent.
        :param parent: Either extg_tree itself or one of its nodes
            (StatementsTreeWidgetNode). At the first call of the method,
            it should be self. The recursion takes care of the rest.
        """

        # If branch is empty, put statement at the end. This occurs when
        # the branch is already created.
        if not branch:
            if self.is_exercise_list:
                item = ChooseExerciseWidgetItem(statement)
            else:
                item = StatementsTreeWidgetItem(statement)
            self.items.append(item)
            root            = item.text(0)
            extg_tree[root] = (item, dict())
            parent.add_child(item)
            return None

        # Else go through the already existing branch and create
        # children nodes if necessary.
        root   = branch[0]   # 'rings'
        branch = branch[1:]  # ['ideals', 'def']
        flag    = expanded_flags[0]
        expanded_flags = expanded_flags[1:]

        if root not in extg_tree:
            node            = StatementsTreeWidgetNode(root)
            extg_tree[root] = (node, dict())
            parent.add_child(node)
            node.setExpanded(flag)  # Must be done AFTER node is added

        self._init_tree_branch(extg_tree[root][1], branch, expanded_flags,
                               statement, extg_tree[root][0])

    def _init_tree(self, statements: [Statement], outline: Dict[str, str]):
        """
        Initiate self's tree given an ordered list of instances of the
        class Statement and the so-called outline (see self.__doc__).
        All the work is done by calling self._init_tree_branch for each
        statement with the right arguments.

        All the tree (structure, nodes, items, titles, etc) is encoded
        as a recursive dictionary. Keys are titles to be displayed and
        values are tuple t, where:
            - t[0] is either an instance of the class
              StatementsTreeWidgetNode or StatementsTreeWidgetItem;
            - t[1] is a dictionary on the same principle.
        Here is an example:

        {'Groups': (StatementsTreeWidgetNode('Groups'),
            {'Subgroups': (StatementsTreeWidgetNode(None, 'Subgroups'),
                {statement.text(0): (statement, dict())})})}

        :param statements: The ordered list of instances of the class
            (or child of) Statement one wants to display.
        :param outline: A Dict[str, str] in which keys are
            hierarchy levels (e.g.  'rings_and_ideals') and values are
            their pretty names (e.g. 'Rings and ideals'), see
            self.__doc__. 
        """

        self._tree = dict()

        # set flags for expandedness: branches will be expanded until
        # a certain depth, and unexpanded after
        depth = StatementsTreeWidget.depth_of_unfold_statements

        for statement in statements:
            branch = statement.pretty_hierarchy(outline)
            # set expanded_flags to True until depth and False after:
            length = len(branch)
            if length >= depth:
                expanded_flags = [True]*depth + [False]*(length-depth)
            else:
                expanded_flags = [True]*length
            self._init_tree_branch(self._tree, branch, expanded_flags,
                                   statement, self)

    def __init__(self, statements: [Statement], outline: Dict[str, str],
                 is_exercise_list=False):
        """
        Init self with a list of instances of the class Statement (or
        child of) and an outline (see self.__doc__). This method
        automatically calls self._init_tree, which itself instantiates
        all the nodes and items in self._init_tree_branch.

        :param statements: The ordered list of instances of the class
            (or child of) Statement one wants to display.
        :param outline: A Dict[str, str] in which keys are
            hierarchy levels (e.g.  'rings_and_ideals') and values are
            their pretty names (e.g. 'Rings and ideals'), see
            self.__doc__. 
        """

        # TODO: get rid of self._init_tree ?
        # IMPORTANT: re-initialize StatementsTreeWidgetItem dictionary
        # StatementsTreeWidgetItem.from_lean_name = {}
        super().__init__()
        self.setColumnCount(2 if is_exercise_list else 1)

        self.is_exercise_list = is_exercise_list
        self._potential_drop_receiver = None
        self._current_dragging_node = None
        self.expand_node_timer = QTimer()
        self.expand_node_timer.timeout.connect(self.expand_current_node)

        self.items: [QTreeWidgetItem] = []  # List of items
        self._init_tree(statements, outline)
        # self.update_tooltips(check_availability=True)
        # By default, drag and drop disabled. See _exercise_main_window_widgets.
        self.setDragEnabled(False)
        self.setAcceptDrops(False)
        self.setDragDropMode(QAbstractItemView.NoDragDrop)

        if cvars.get('functionality.drag_statements_to_context', True):
            self.setDragEnabled(True)
            self.setDragDropMode(QAbstractItemView.DragOnly)
        else:
            self.setDragEnabled(False)
        # Drops in statements:
        if cvars.get('functionality.drag_context_to_statements', True):
            self.setAcceptDrops(True)
            self.setDragDropMode(QAbstractItemView.DropOnly)
        else:
            self.setAcceptDrops(False)
        if cvars.get('functionality.drag_context_to_statements', True) \
                and cvars.get('functionality.drag_statements_to_context', True):
            self.setDragDropMode(QAbstractItemView.DragDrop)

        # Cosmetics
        self.setWindowTitle('StatementsTreeWidget')
        if self.is_exercise_list:
            self.setHeaderLabels([_('Exercises'), _('Saved proofs')])
        else:
            self.setHeaderLabels([_('Statements')])

        self.expandToDepth(3)  # To get reasonable column size
        self.resizeColumnToContents(0)
        self.expandToDepth(self.depth_of_unfold_statements)

        # Modify color for selected objects
        palette = self.palette()
        background_color = cvars.get("display.color_for_selection", "limegreen")
        highlight_color = QColor(background_color)
        palette.setBrush(palette.Normal, palette.Highlight, highlight_color)
        palette.setBrush(palette.Inactive, palette.Highlight, highlight_color)
        self.setPalette(palette)

    def add_child(self, item):
        """
        Called in self._init_tree_branch, do not delete!  Useful not to
        have to make a difference between self.addTopLevelItem when we
        add an item to the tree itself or parent.add_child when we add
        an item to a parent which is a tree item.

        :param item: Either a StatementsTreeWidgetItem or a
            StatementsTreeWidgetNode.
        """

        self.addTopLevelItem(item)

    def goto_statement(self, statement: Optional[Statement], expand=True):
        """
        Go to the Statement statement (as if usr clicked on it).
        If statement is None then go to the first Exercise.
        :param statement: Statement to go to.
        :param expand: if True, reveal statement by expanding all parents items.
        """
        log.debug("goto exercise")
        # Thanks @mcosta from https://forum.qt.io/topic/54640/
        # how-to-traverse-all-the-items-of-qlistwidget-qtreewidget/3

        def traverse_node(item: StatementsTreeWidgetItem):
            # Do something with item
            if isinstance(item, StatementsTreeWidgetItem):
                if ((isinstance(statement, Exercise)
                     and (statement.is_copy_of(item.statement)
                          or item.statement == statement))
                    or (statement is None
                        and isinstance(item.statement, Exercise))):
                    self.setCurrentItem(item)
                    return True
            for i in range(0, item.childCount()):
                if traverse_node(item.child(i)):
                    item.setExpanded(expand)
                    return True
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if traverse_node(item):
                item.setExpanded(expand)
                break

        self.setFocus()

    @staticmethod
    def item_from_lean_name(lean_name: str) -> StatementsTreeWidgetItem:
        """
        Return the StatementsTreeWidgetItem whose statement's Lean name is
        lean_name.
        """
        return StatementsTreeWidgetItem.from_lean_name.get(lean_name)

    def item_from_statement(self, statement):
        return self.item_from_lean_name(statement.lean_name)

    def hide_statements(self, statements: [Statement], yes=True):
        """
        Hide all the provided statements. Based on item_from_statement.
        """
        for statement in statements:
            item = self.item_from_statement(statement)
            if item:
                item.setHidden(yes)

    def index_from_event(self, event):
        return self.indexAt(event.pos())

    def item_from_index(self, index_):
        item = self.itemFromIndex(index_)
        return item

    def select_index(self, index, yes=True):
        self.setItemSelected(self.item_from_index(index), yes)

    @Slot()
    def update_tooltips(self, check_availability=False):
        for item in self.items:
            item.parent = self
            item.set_tooltip(check_availability=check_availability)

    @property
    def potential_drop_receiver(self):
        return self._potential_drop_receiver

    @potential_drop_receiver.setter
    def potential_drop_receiver(self, receiver: QModelIndex):
        if (self.potential_drop_receiver and
                receiver != self.potential_drop_receiver):
            self.select_index(self._potential_drop_receiver, False)
            self._potential_drop_receiver = None
        if receiver and receiver not in self.selectedIndexes():
            self._potential_drop_receiver = receiver
            self.select_index(receiver)

    def expand_current_node(self):
        if self._current_dragging_node:
            self._current_dragging_node.setExpanded(True)
            self._current_dragging_node = None

    def dragEnterEvent(self, event):
        """
        Accept drag except if it comes from self.
        """
        source = event.source()
        if not isinstance(source, StatementsTreeWidget):
            event.acceptProposedAction()

    def dragMoveEvent(self, event) -> None:
        """
        When a MathWidgetItem is dragged over a potential receiver, select it
        temporarily.
        """

        self.expand_node_timer.stop()
        index = self.index_from_event(event)
        if index != self.potential_drop_receiver:
            self.potential_drop_receiver = None  # Unselect automatically

        # if index:
        item = self.item_from_index(index)
        if item:  # and item.isDropEnabled():
            self.potential_drop_receiver = index

        if item and item.is_node:
            self._current_dragging_node = item
            self.expand_node_timer.start(500)

        event.accept()

    def dragLeaveEvent(self, event) -> None:
        self.expand_node_timer.stop()
        self.potential_drop_receiver = None  # Unselect automatically
        # print("dragLeave statement")

    def dropEvent(self, event):
        """
        Process MathWidgetItem dropped on statements.
        """
        # Not activated.
        source = event.source()
        if isinstance(source, StatementsTreeWidget):  # Should not happen
            event.accept()
            # self.clearSelection()
            return
        else:
            dragged_index = source.currentIndex()
            index = self.index_from_event(event)
            item = self.itemFromIndex(index)
            if not item or item.is_node:  # Not dropped on a statement
                return
            # print(f"Source : {source}, dragged index: {dragged_index}")
            # print(f"Source selected items: {len(source.selected_items())}")
            if dragged_index not in source.selectedIndexes():
                source.select_index(dragged_index)
            # Emit signal
            self.math_object_dropped.emit(item)

        self.setDropIndicatorShown(False)
        event.accept()

    def mouseMoveEvent(self, event) -> None:
        """
        Clear selection to avoid meaningless selected items.
        """
        super().mouseMoveEvent(event)
        if not self.state() == QAbstractItemView.DraggingState:
            QTimer.singleShot(1, self.clearSelection)

    # def clear_current_index(self):
    #     self.setCurrentIndex(QModelIndex())
    #
    # def currentChanged(self, current, previous) -> None:
    #     """
    #     Prevent current index setting (which has no meaning and would be
    #     highlighted in light blue).
    #     """
    #     if not self.state() == QAbstractItemView.DraggingState:
    #         QTimer.singleShot(1, self.clear_current_index)

    # def event(self, event: QEvent):
    #     """
    #     Re-implement event handler to show dynamic tooltips.
    #     """
    #     log.debug(f"Event {event.type} handled by QtreeWidget")
    #     log.debug(event)
    #     if event.type == QEvent.ToolTip:
    #         log.debug("Showing tooltip")
    #         pos = QHelpEvent.globalPos(event)
    #         item = self.itemAt(pos)
    #         text = item.statement.caption
    #         QToolTip.showText(pos, text)
    #         event.accept()
    #         return True
    #     else:
    #         pass
    #         # Propagate event
    #         # QToolTip.hideText()
    #         event.ignore()
    #         if isinstance(event, QTimerEvent):
    # The following does not work, which drives me crazy:
    #             return QObject.timerEvent(event)
    #         else:
    #             return QTreeWidget.event(event)
