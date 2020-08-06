"""
###################################################################
# actions_widgets_classes.py : actions widgets for ExerciseWidget #
###################################################################

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
from typing import  Dict,

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

from deaduction.pylib.actions    import   Action
from deaduction.pylib.coursedata import ( Definition,
                                          Exercise,
                                          Statement,
                                          Theorem)

log = logging.getLogger(__name__)

#################################
# Action button widgets classes #
#################################

# Classes for the two rows of buttons (e.g. ∀ button) in the 'Actions'
# area of the exercise window. Each button is coded as an instance of
# the class ActionButton and and each row essentially is a container of
# instances of ActionButton coded as an instance of ActionButtonsWidget.


class ActionButton(QPushButton):
    """
    ActionButton is the class for so-called 'action buttons' (e.g. ∀
    button): it takes an instance of the Action class and associates it
    to a button. It contains all relevant information that L∃∀N needs to
    use this action in its atribute self.action. Since each instance of
    the class Action also has a symbol and a caption as attributes, one
    just needs an instance of the class Action to instanciate a
    ActionButton.

    :attribute action (Action): The instance of the Action class that self was
        instanciated with.
    :attribute action_triggered (Signal(ActionButton)): A Signal with
        self as an argument, emited when self is clicked on.
    """

    def __init__(self, action: Action):
        """
        Instanciate an ActionButton with an instance of the class
        Action. Set text, tooltip and keep the given action as an
        attribute. When self is clicked on, emit the signal
        self.action_triggered.

        :param action Action: An instance of the class Action.
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
        One can see in ActionButton.__init__ that this slot is connected
        to ActionButton.clicked signal, and is therefore when self is
        pressed on.
        """

        self.action_triggered.emit(self)


# Required to have an ActionButton as an argument in an ActionButton.
# Writting 
# self.action_triggered = Signal(ActionButton)
# in ActionButton.__init__ will raise an exception.
ActionButton.action_triggered = Signal(ActionButton)


class ActionButtonsWidget(QWidget):
    """
    A container class to create and display an ordered row of instances
    of the class ActionButton given a list of instances of the class
    ActionButton.

    :param buttons [ActionButton]: The list of instances of the class
    ActionButton created and displayed in self.__init__. This attribute
    makes accessing them painless.
    """

    def __init__(self, actions: [Action]):
        """
        Init self with an ordered list of instances the class Action.

        :param actions: The list of instances of the class Action one
            wants to create buttons from.
        """

        super().__init__()

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
# coded in the following classes. Those statements are represented in a
# tree (StatementsTreeWidget) preserving the course structure:
#   - each node (StatementsTreeWidgetNode) corresponds to a section;
#   - each leaf (StatementsTreeWidgetItem) corresponds to a statement.
# Even though StatementsTreeWidgetItem and StatementsTreeWidgetNode are
# not protected nor private, they should not be instanciated outside
# this module. Furthermore the so-called 'statements tree' is
# automatically created by StatementsTreeWidget.__init__ given an
# ordered list of instances of the Statement class and it is this
# method which instanciates the items and nodes.


class StatementsTreeWidgetItem(QTreeWidgetItem):
    """
    This class is a tree item (inherits from QTreeWidgetItem) in charge
    of displaying an instance of the class Statement (or child class).
    It contains all relevant information that L∃∀N needs to use this
    statement in its atribute self.statement. Since this statement also
    contains data to be displayed (e.g. a title), one only needs an
    instance of the class Statement to instanciate a
    StatementsTreeWidgetItem.

    :attribute statement Statement: The instance of the class Statement
        associated to self.
    """

    def __init__(self, statement: Statement):
        """
        Init self with an instance of the Statement class.

        :parem statement: An instance of the Statement class.
        """

        super().__init__(None, [statement.pretty_name, statement.lean_name])

        self.statement = statement

        # Print second col. in gray
        self.setForeground(1, QBrush(QColor('gray')))

        # Print icon (D for definition, T for theorem, etc)
        icons_path = Path('share/graphical_resources/icons/letters')
        if isinstance(statement, Definition):
            path = icons_path / 'd.png'
        elif isinstance(statement, Exercise):
            path = icons_path / 'e.png'
        elif isinstance(statement, Theorem):
            path = icons_path / 't.png'
        self.setIcon(0, QIcon(str(path.resolve())))


class StatementsTreeWidgetNode(QTreeWidgetItem):
    """
    This class renders a hierarchical element of the course (e.g. a
    section) as an unclickable node in the statements tree. Statements
    (StatementsTreeWidgetItem) are children of those nodes. For example,
    given the section name 'Finite groups', self is a node with title
    'Finite groups'.
    """

    def __init__(self, title: str):
        """
        Init self with a title.

        :parem title: The title to be displayed.
        """

        # QTreeWidget objects use columns to display titles. So if one
        # wants to display a unique title, it needs to be in a 1-element
        # list.
        super().__init__(None, [title])

        # Cosmetics
        self.setExpanded(True)
        self.set_selectable(False)

    def set_selectable(self, yes: bool=True):
        """
        Make self to be selectable if yes or unselectable otherwise.
        There is no built-in method for this so we use flags as if we
        are in 1980 (thanks Florian).

        :param yes: See above.
        """

        if yes:
            new_flags = self.flags() &  Qt.ItemIsSelectable
        else:
            new_flags = self.flags() & ~Qt.ItemIsSelectable
        self.setFlags(new_flags)


class StatementsTreeWidget(QTreeWidget):
    """
    This class renders an ordered list of instances of the class
    Statement as a tree (inherits from QTreeWidget). The nodes
    correspond to hierarchical elements (e.g. sections) and the leaves
    to statements in this hierarchy. This class is instanciated with a
    list of instances of the class Statement and what we called an
    outline, which is just a dictionnary (most of the time
    Exercise.outline attribute) of which keys are hierarchy levels and
    values are pretty names for display. Furthermore, all relevant
    information that L∃∀N needs to use those statements is stored in
    them and one does not need anything else appart from the outline to
    create the so-called statements tree.

    Here is an example, if we give ourselves an ordered list of three
    statements with the following lean names:
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
    (D) and (T) are icons which enable to differenciate definitions,
    theorems and exercises. Note that statements pretty names (which
    enable to display 'Lagranges's theorem instead of 'lagrange') are
    not in the outline, they are already coded in the instances of the
    class Statement themselves with the attribute pretty_name.
    """

    def __init__(self, statements: [Statement], outline: Dict[str, str]):
        """
        Init self with a list of statements and an outline, see
        self.__doc__ above. This method automatically calls
        self._init_tree, which itself instanciates all the nodes and
        items in self.init_branch.

        :param statements: An ordered list of instances of the Statement
            class.
        :param outline: A dictionnary in which keys are
            hierarchy levels (e.g.  'rings_and_ideals') and values are
            their pretty names (e.g. 'Rings and ideals'). 
        """

        super().__init__()
        self._init_tree(statements, outline)

        # Cosmetics
        self.setAlternatingRowColors(True)
        self.setHeaderLabels([_('Statement'), _('L∃∀N name')])
        self.setWindowTitle('StatementsTreeWidget')
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)

    def addChild(self, item):
        """
        Called in self._init_branch_statement, do not delete!  Usefull
        not to have to make a difference between self.addTopLevelItem
        when we add an item to the tree itself or parent.addChild when
        we add an item to a parent which is a tree item.

        :param item: Either a StatementsTreeWidgetItem or a
            StatementsTreeWidgetNode.
        """

        self.addTopLevelItem(item)

    def _init_branch_statement(self, extg_tree, branch: [str],
                               statement: Statement, parent):
        """
        Add branch to extg_tree and statement at the end of branch. This
        function is recursive.

        :param extg_tree: A tree implemented as a reccursive
            dictionnary, see self._init_tree.__doc__.
        :param branch: A tree branch (new or already existing), e.g.
            ['Chapter', 'Section', 'Sub-section'].
        :param statement: The instance of the
            classStatementsTreeWidgetItem to be added at the end of
            branch.
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
            parent.addChild(item)
            return None

        # Else go through the already existing branch and create
        # children nodes if necessary.
        root   = branch[0]   # 'rings'
        branch = branch[1:]  # ['ideals', 'def']

        if root not in extg_tree:
            node            = StatementsTreeWidgetNode(root)
            extg_tree[root] = (node, dict())
            parent.addChild(node)
            node.setExpanded(True)  # Must be done AFTER node is added

        self._init_branch_statement(extg_tree[root][1], branch,
                                    statement, extg_tree[root][0])

    def _init_tree(self, statements: [Statement], outline: Dict[str, str]):
        """

        Initiate the tree part of self (which derives from QTreeWidget)
        given an ordered list of instances of the class Statement and
        the so-called outline (see self.__doc__). All the work is done
        by calling self._init_branch_statement for each statement with
        the right arguments.

        All the tree (structure, nodes, items, titles, etc) is encoded
        as a reccursive dictionnary. Keys are titles to be displayed and
        values are tuple t, where:
            - t[0] is either an instance of the class
              StatementsTreeWidgetNode or StatementsTreeWidgetItem;
            - t[1] is a dictionnary on the same principle.
        Here is an example:

        {'Groups': (StatementsTreeWidgetNode('Groups'),
            {'Subgroups': (StatementsTreeWidgetNode(None, 'Subgroups'),
                {statement.text(0): (statement, dict())})})}

        :param statements: An ordered list of instances of the Statement
            class.
        :param outline: A dictionnary in which keys are
            hierarchy levels (e.g.  'rings_and_ideals') and values are
            their pretty names (e.g. 'Rings and ideals'), see
            self.__doc__.
        """

        self._tree = dict()

        for statement in statements:
            branch = statement.pretty_hierarchy(outline)
            self._init_branch_statement(self._tree, branch, statement, self)
