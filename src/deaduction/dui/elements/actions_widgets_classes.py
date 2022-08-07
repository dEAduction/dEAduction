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
        - ActionButtonsWidget;
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

import              logging
from typing import  Dict
from trio import sleep

from PySide2.QtGui     import ( QBrush,
                                QColor,
                                QIcon,
                                QCursor,
                                QHelpEvent)
from PySide2.QtCore    import ( Signal,
                                Slot,
                                Qt,
                                QEvent,
                                QObject,
                                QTimerEvent)
from PySide2.QtWidgets import ( QHBoxLayout,
                                QPushButton,
                                QWidget)
from PySide2.QtWidgets import ( QTreeWidget,
                                QTreeWidgetItem,
                                QToolTip)

from deaduction.pylib.text        import ( button_symbol,
                                           button_tool_tip)

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
# instances of ActionButton coded as an instance of ActionButtonsWidget.


class ActionButton(QPushButton):
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
    from_name: dict = {}  # name -> ActionButton
    # ! Must be updated to avoid pointing to deleted items !

    def __init__(self, action: Action):
        """
        Init self with an instance of the class Action. Set text,
        tooltip and keep the given action as an attribute. When self is
        clicked on, emit the signal self.action_triggered.

        :param action: The instance of the class Action one wants
            self to be associated with.
        """

        super().__init__()

        self.action = action
        self.update()  # set symbol and tool tip
        self.clicked.connect(self._emit_action)
        # Modify arrow appearance when over a button
        self.setCursor(QCursor(Qt.PointingHandCursor))
        # Update dictionary:
        # self.from_name[action.symbol] = self
        self.from_name[action.name] = self

    def update(self):
        """
        Set or update text and tooltips in button, using module pylib.text.
        NB: translation is done here.
        """
        name = self.action.name
        symbol = _(button_symbol(name))
        self.setText(symbol)
        # if len(symbol) > 1:
        #     self.setStyleSheet('QPushButton { font-size: 12pt }')

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
        self.setToolTip(tooltip)

    @Slot()
    def _emit_action(self):
        """
        Emit the signal self.action_triggered with self as an argument.
        This slot is connected to ActionButton.clicked signal in
        self.__init__.
        """

        self.action_triggered.emit(self)

    @property
    def symbol(self):
        """
        Actual text displayed on self (may be changed by usr).
        """
        return self.action.symbol

    @property
    def name(self):
        """
        (Immutable) name of the corresponding action.
        One of  ['and', 'or', 'not', 'implies', 'iff', 'forall', 'exists',
                 'equal', 'map']
        """
        return self.action.name

    def has_symbol(self, symbol) -> bool:
        """
        Test if symbol is the symbol of (the action associated to) self.
        """
        # TODO: obsolete (?)
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


# We wish to have an ActionButton class attribute called
# action_triggered and defined as Signal(ActionButton). At first, one
# may define it in ActionButton.__init__. However, doing this will raise
# an exception because in ActionButton.__init__, the class ActionButton
# is not *yet* defined. The workaround is to define this class attribute
# outside of the class definition, as followed.
ActionButton.action_triggered = Signal(ActionButton)


class ActionButtonsWidget(QWidget):
    """
    A container class to create and display an ordered row of instances
    of the class Action as buttons (instances of the class
    ActionButton). Each element of this list inits an instance of the
    class ActionButton; this instance is set to be a child of self and
    is kept as an attribute in self.buttons.

    :param buttons [ActionButton]: The list of instances of the class
        ActionButton created and displayed in self.__init__. This
        attribute makes accessing them painless.
    """

    def __init__(self, actions: [Action]):
        """
        Init self with an ordered list of instances of the class Action.

        :param actions: The list of instances of the class Action one
            wants to create buttons from.
        """

        super().__init__()

        # TODO: make self.buttons a property?
        self.buttons = []

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        for action in actions:
            action_button = ActionButton(action)
            main_layout.addWidget(action_button)
            self.buttons.append(action_button)

        main_layout.addStretch()

        self.setLayout(main_layout)

    def update(self):
        """
        Update text and tooltips in all buttons.
        """
        # Fixme: obsolete
        for button in self.buttons:
            button.update()


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
    from_lean_name : dict = {}  # Statement.lean_name --> item
    # ! Must be updated to avoid pointing to deleted items !

    def __init__(self, statement: Statement):
        """
        Init self with an instance of the class (or child of) Statement.

        :param statement: The instance of the class (or child) one wants
            to associate to self.
        """
        if StatementsTreeWidget.show_lean_name_for_statements:
            to_display = [statement.pretty_name, statement.lean_name]
        else:
            to_display = [statement.pretty_name]

        super().__init__(None, to_display)

        self.statement = statement
        self.parent = None  # Will be the QTreeWidget when inserted

        # Print second col. in gray
        self.setForeground(1, QBrush(QColor('gray')))
        # TODO: use mono font for lean name column (column 1)

        # Print icon (D for definition, T for theorem, etc)
        icons_base_dir = cvars.get("icons.path")
        icons_type     = cvars.get("icons.letter_type")

        icons_dir = fs.path_helper(icons_base_dir) / icons_type
        if isinstance(statement, Definition):
            path = icons_dir / 'd.png'
        elif isinstance(statement, Exercise):
            path = icons_dir / 'e.png'
        elif isinstance(statement, Theorem):
            path = icons_dir / 't.png'
        self.setIcon(0, QIcon(str(path.resolve())))

        self.from_lean_name[statement.lean_name] = self

        # Set tooltips: tooltips are set when item is put in the QTReeWidget
        # so that is_exercise property has a meaning
        # self.set_tooltip()

    @property
    def is_exercise(self):
        if self.parent:
            return self.parent.is_exercise_list

    def is_node(self):
        return False

    def set_tooltip(self):
        """
        Set the math content of the statement as tooltip.
        """
        self.setToolTip(0, self.statement.caption(
            is_exercise=self.is_exercise))
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
        if expand:
            self.setExpanded(expand)
            self.treeWidget().scrollToItem(self)
        duration = duration /(3*winkle_nb)
        for n in range(winkle_nb):
            self.setBackground(0, QBrush(QColor('blue')))
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


class StatementsTreeWidgetNode(QTreeWidgetItem):
    """
    This class renders a hierarchical element of the course (e.g. a
    section) as an unclickable node in the so-called 'statements tree'.
    Statements (StatementsTreeWidgetItem) are children of those nodes.
    For example, given the section name 'Finite groups', self is a node
    with title 'Finite groups'.
    """

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
        # self.set_selectable(False)

    # @property
    # def is_exercise_list(self):
    #     if self.parent():
    #         return self.parent().is_exercise_list

    def is_node(self):
        return True

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

    # TODO: Put this in self.__init__
    # Config
    depth_of_unfold_statements = \
                        cvars.get("display.depth_of_unfold_statements")

    show_lean_name_for_statements = \
                    cvars.get("display.show_lean_name_for_statements")

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
            item            = StatementsTreeWidgetItem(statement)
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
        StatementsTreeWidgetItem.from_lean_name = {}
        super().__init__()
        self.items: [QTreeWidgetItem] = [] # List of items
        self._init_tree(statements, outline)
        self.is_exercise_list = is_exercise_list
        self.update_tooltips()
        # Uncomment to enable drag:
        # self.setDragEnabled(True)

        # Cosmetics
        self.setWindowTitle('StatementsTreeWidget')
        if StatementsTreeWidget.show_lean_name_for_statements:
            self.setHeaderLabels([_('Statements'), _('L∃∀N name')])
            self.resizeColumnToContents(0)
            self.resizeColumnToContents(1)
        else:
            self.resizeColumnToContents(0)
            self.setHeaderLabels([_('Statements')])

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

    def goto_statement(self, statement: Statement, expand=True):
        """
        Go to to the Statement statement (as if usr clicked on it).

        :param statement: Statement to go to.
        :param expand: if True, expandreveal statement by expanding all
        parents items.
        """
        log.debug("goto exercise")
        # Thanks @mcosta from https://forum.qt.io/topic/54640/
        # how-to-traverse-all-the-items-of-qlistwidget-qtreewidget/3

        def traverse_node(item: StatementsTreeWidgetItem):
            # Do something with item
            if isinstance(item, StatementsTreeWidgetItem):
                if item.statement == statement:
                    item.setSelected(True)
                    return True
            for i in range(0, item.childCount()):
                if traverse_node(item.child(i)):
                    item.setExpanded(expand)
                    return True
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if traverse_node(item):
                item.setExpanded(expand)

    @staticmethod
    def item_from_lean_name(lean_name: str) -> StatementsTreeWidgetItem:
        """
        Return the StatementsTreeWidgetItem whose statement's pretty name is
        pretty_name.
        """
        return StatementsTreeWidgetItem.from_name.get(lean_name)

        # items = []
        #
        # def traverse_node(item: StatementsTreeWidgetItem):
        #     if isinstance(item, StatementsTreeWidgetItem):
        #         if item.statement.has_name(lean_name):
        #             items.append(item)
        #     for i in range(0, item.childCount()):
        #         traverse_node(item.child(i))
        #
        # for i in range(self.topLevelItemCount()):
        #     item = self.topLevelItem(i)
        #     traverse_node(item)
        # if items:
        #     return items[0]
        # else:
        #     return None

    def item_from_statement(self, statement):
        return self.item_from_lean_name(statement.lean_name)

    @Slot()
    def update_tooltips(self):
        for item in self.items:
            item.parent = self
            item.set_tooltip()

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
