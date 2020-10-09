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

from gettext import gettext as _
import              logging
from pathlib import Path
from typing import  Dict

from PySide2.QtGui     import ( QBrush,
                                QColor,
                                QIcon)
from PySide2.QtCore    import ( Signal,
                                Slot,
                                Qt)
from PySide2.QtWidgets import ( QHBoxLayout,
                                QPushButton,
                                QWidget)
from PySide2.QtWidgets import ( QTreeWidget,
                                QTreeWidgetItem)

from deaduction.config.config import user_config
from deaduction.pylib.actions    import   Action
from deaduction.pylib.coursedata import ( Definition,
                                          Exercise,
                                          Statement,
                                          Theorem)
from deaduction.dui.utils        import   set_selectable

log = logging.getLogger(__name__)

#################################
# Action button widgets classes #
#################################

# Classes for the two rows of buttons (e.g. ∀ button) in the Actions
# area of the exercise window. Each button is coded as an instance of
# the class ActionButton and each row essentially is a container of
# instances of ActionButton coded as an instance of ActionButtonsWidget.


class ActionButton(QPushButton):
    """
    Class for so-called 'action buttons' (e.g. ∀ button). Each
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

        self.setText(action.symbol)
        self.setToolTip(action.caption)
        self.clicked.connect(self._emit_action)

    @Slot()
    def _emit_action(self):
        """
        Emit the signal self.action_triggered with self as an argument.
        This slot is connected to ActionButton.clicked signal in
        self.__init__.
        """

        self.action_triggered.emit(self)


# We wish to have an ActionButton class attribute called
# action_triggered and defined as Signal(ActionButotn). At first, one
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
        for action in actions:
            action_button = ActionButton(action)
            main_layout.addWidget(action_button)
            self.buttons.append(action_button)
        self.setLayout(main_layout)


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

    def __init__(self, statement: Statement):
        """
        Init self with an instance of the class (or child of) Statement.

        :param statement: The instance of the class (or child) one wants
            to associate to self.
        """

        super().__init__(None, [statement.pretty_name, statement.lean_name])

        self.statement = statement

        # Print second col. in gray
        self.setForeground(1, QBrush(QColor('gray')))
        # TODO: use mono font for lean name column (column 1)

        # Print icon (D for definition, T for theorem, etc)
        icons_path = Path('share/graphical_resources/icons/letters')
        if isinstance(statement, Definition):
            path = icons_path / 'd.png'
        elif isinstance(statement, Exercise):
            path = icons_path / 'e.png'
        elif isinstance(statement, Theorem):
            path = icons_path / 't.png'
        self.setIcon(0, QIcon(str(path.resolve())))

        # Set tooltip
        self.setToolTip(0, statement.caption)


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
        self.setExpanded(True)
        self.set_selectable(False)

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
        depth = user_config.getint('depth_of_unfold_statements')

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

    def __init__(self, statements: [Statement], outline: Dict[str, str]):
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

        #TODO: get rid of self._init_tree ?

        super().__init__()
        self._init_tree(statements, outline)

        # Cosmetics
        self.setHeaderLabels([_('Statement'), _('L∃∀N name')])
        self.setWindowTitle('StatementsTreeWidget')
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)

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
