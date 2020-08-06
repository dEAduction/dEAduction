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
    button). It inherits from the class QPushButton. This class contains
    all relevant information that L∃∀N needs to 'understand' the button
    in its atribute self.action. Since each instance of the class Action
    also has a symbol and a caption as attributes, one just needs an
    instance of the class Action to instanciate a ActionButton.

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

        :param action: An instance of the class Action.
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
# Defining 
# self.action_triggered = Signal(ActionButton)
# in ActionButton.__init__ will raise an exception.
ActionButton.action_triggered = Signal(ActionButton)


class ActionButtonsWidget(QWidget):

    def __init__(self, actions: [Action]):
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


class StatementsTreeWidgetItem(QTreeWidgetItem):

    def _initUI(self):
        # Print second col. in gray
        self.setForeground(1, QBrush(QColor('gray')))

    def __init__(self, statement: Statement):
        """

        :parem statement: An instance of the Statement class.
        """

        self.statement = statement
        titles = [statement.pretty_name, statement.lean_name]
        super().__init__(None, titles)
        self._initUI()

        icon_path = Path('share/graphical_resources/icons/letters')
        if isinstance(statement, Definition):
            path = icon_path / 'd.png'
        elif isinstance(statement, Exercise):
            path = icon_path / 'e.png'
        elif isinstance(statement, Theorem):
            path = icon_path / 't.png'

        self.setIcon(0, QIcon(str(path.resolve())))


class StatementsTreeWidgetNode(QTreeWidgetItem):

    def _initUI(self):
        self.setExpanded(True)
        icon_path = Path('share/graphical_resources/icons/folder.png')
        icon = QIcon(str(icon_path.resolve()))
        self.setIcon(0, icon)

    def __init__(self, titles):
        """

        :parem titles: A list of column titles. It must not be a str.
        """

        super().__init__(None, titles)
        self._initUI()
        self.set_selectable(False)

    def set_selectable(self, yes=True):
        # Thanks Florian, there is no method for this so we use a QFlag
        if yes:
            new_flags = self.flags() & Qt.ItemIsSelectable
        else:
            new_flags = self.flags() & ~Qt.ItemIsSelectable

        self.setFlags(new_flags)


class StatementsTreeWidget(QTreeWidget):

    def __init__(self, statements, outline):
        """

        :param statements: An ordered list of instances of the Statement class.
        :param outline: A dictionnary in which keys are hierarchy levels (e.g.
                'rings_and_ideals') and values are their pretty names
                (e.g. 'Rings and ideals').
        """
        super().__init__()
        self._initUI()
        self.init_tree(statements, outline)

    def _initUI(self):
        self.setAlternatingRowColors(True)
        self.setHeaderLabels([_('Statements')])
        self.setWindowTitle('StatementsTreeWidget')

    def addChild(self, item):
        """
        Usefull in self._init_statement, do not delete!
        Usefull not to have to make a difference between self.addTopLevelItem
        when we add an item to the tree itself or parent.addChild when we add
        an item to a parent which is a tree item.

        :param item: Either a StatementsTreeWidgetItem or a
                StatementsTreeWidgetNode.
        """

        self.addTopLevelItem(item)

    def _init_statement(self, extg_tree, statement, branch, parent=None):
        """
        Add a branch to extg_tree and statement at the end of this branch.

        :param extg_tree: A dictionnary that looks like this:
                {'Groups': (StatementsTreeWidgetNode('Groups'),
                    {'Finite groups': (StatementsTreeWidgetNode(None,
                                                          'Finite groups'),
                        {statement.text(0): (statement, dict()
                        )}
                    )}
                )}
        :param statement: An instance of StatementsTreeWidgetItem.
        :param branch: A branch (new or already existing) as a list of str,
                e.g.  ['Chapter', 'Section', 'Sub-section'].
        :param parent: A StatementsTreeWidgetNode or extg_tree itself (at
                the first call of the function). Either branch or statement
                is added as a child of parent.
        """

        # If branch is empty, put statement at the end
        if not branch:
            item = StatementsTreeWidgetItem(statement)
            root = item.text(0)
            extg_tree[root] = (item, dict())
            parent.addChild(item)
            return None

        # Else go through the already existing branch or create the nodes
        root = branch[0]        # 'rings'
        branch = branch[1:]     # ['ideals', 'def']

        if root not in extg_tree:
            node = StatementsTreeWidgetNode([root])
            extg_tree[root] = (node, dict())
            parent.addChild(node)
            node.setExpanded(True)  # Must be done AFTER node added

        self._init_statement(extg_tree[root][1], statement,
                             branch, extg_tree[root][0])

    def init_tree(self, statements, outline):
        """
        Initiate the tree of StatementsTreeWidget (derives from
        QTreeWidget)given an ordered list of instances of Statement. The branch
        where a statement must be put is already encoded in its lean_name
        attribute, e.g.  'chapter.section.sub_section.statement'. But we do not
        want to print ugly lean_names for sections (e.g. 'rings_and_ideals'),
        what we want is instead pretty names (e.g. 'Rings and ideals').
        Therefore we have outline, a dictionnary which to any level of
        hierarchy (e.g. chapter) associates its pretty name.

        :param statements: An ordered list of instances of the Statement class.
        :param outline: A dictionnary in which keys are hierarchy levels (e.g.
                'rings_and_ideals') and values are their pretty names
                (e.g. 'Rings and ideals').
        """

        self._tree = dict()

        for statement in statements:
            branch = statement.pretty_hierarchy(outline)
            self._init_statement(self._tree, statement, branch, self)
