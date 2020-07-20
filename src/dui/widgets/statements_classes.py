"""
#####################################################################
# statements_classes.py : provide classes for the statements widget #
#####################################################################

    This file provides StatementsTreeItem, StatementsTreeNode and 
    StatementsTree.

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

from PySide2.QtGui import QBrush, QColor, QIcon
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem


class StatementsTreeItem(QTreeWidgetItem):

    def __init__(self, titles):
        """

        :parem titles: A list of column titles. It must not be a str.
        """

        super().__init__(None, titles)
        self._initUI()

    def _initUI(self):
        self.setExpanded(True)
        # Print second col. in gray
        self.setForeground(1, QBrush(QColor('gray')))

    @classmethod
    def from_Statement(cls, statement):
        """

        :param statement: An instance of the Statement class.
        """

        titles = [statement.pretty_name, statement.identifier]
        instance = cls(titles)

        return instance


class StatementsTreeNode(QTreeWidgetItem):

    def __init__(self, titles):
        """

        :parem titles: A list of column titles. It must not be a str.
        """

        super().__init__(None, titles)
        self._initUI()
        self.setUnselectable()

    def _initUI(self):
        self.setExpanded(True)
        icon = QIcon('icon.png')
        self.setIcon(0, icon)

    def setUnselectable(self):
        # Thanks Florian, there is no method for this so we use a QFlag
        flags = self.flags()
        new_flags = flags & ~Qt.ItemIsSelectable
        self.setFlags(new_flags)


class StatementsTree(QTreeWidget):

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
        self.setWindowTitle('StatementsTree')

    def addChild(self, item):
        """
        Usefull in self._init_statement, do not delete!
        Usefull not to have to make a difference between self.addTopLevelItem
        when we add an item to the tree itself or parent.addChild when we add
        an item to a parent which is a tree item.

        :param item: Either a StatementsTreeItem or a StatementsTreeNode.
        """

        self.addTopLevelItem(item)

    def _init_statement(self, extg_tree, statement, branch, parent=None):
        """
        Add a branch to extg_tree and statement at the end of this branch.

        :param extg_tree: A dictionnary that looks like this:
                {'Groups': (StatementsTreeNode('Groups'),
                    {'Finite groups': (StatementsTreeNode(None, 
                                                          'Finite groups'),
                        {statement.text(0): (statement, dict()
                        )}
                    )}
                )}
        :param statement: An instance of StatementsTreeItem.
        :param branch: A branch (new or already existing) as a list of str,
                e.g.  ['Chapter', 'Section', 'Sub-section'].
        :param parent: A StatementsTreeNode or extg_tree itself (at the first
                call of the function). Either branch or statement is added as
                a child of parent.
        """

        # If branch is empty, put statement at the end
        if not branch:
            item = StatementsTreeItem.from_Statement(statement)
            root = item.text(0)
            extg_tree[root] = (item, dict())
            parent.addChild(item)
            return None

        # Else go through the already existing branch or create the nodes
        root = branch[0]        # 'rings'
        branch = branch[1:]     # ['ideals', 'def']

        if root not in extg_tree:
            extg_tree[root] = (StatementsTreeNode([root]), dict())
            parent.addChild(extg_tree[root][0])

        self._init_statement(extg_tree[root][1], statement,
                             branch, extg_tree[root][0])

    def init_tree(self, statements, outline):
        """
        Initiate the tree of StatementsTree (derives from QTreeWidget) given an
        ordered list of instances of Statement. The branch where a statement
        must be put is already encoded in its lean_name attribute, e.g.
        'chapter.section.sub_section.statement'. But we do not want to print
        ugly lean_names for sections (e.g. 'rings_and_ideals'), what we want is
        instead pretty names (e.g. 'Rings and ideals'). Therefore we have
        outline, a dictionnary which to any level of hierarchy (e.g. chapter)
        associates its pretty name.

        :param statements: An ordered list of instances of the Statement class.
        :param outline: A dictionnary in which keys are hierarchy levels (e.g.
                'rings_and_ideals') and values are their pretty names
                (e.g. 'Rings and ideals').
        """

        self._tree = dict()

        for statement in statements:
            branch = statement.pretty_hierarchy(outline)
            self._init_statement(self._tree, statement, branch, self)
