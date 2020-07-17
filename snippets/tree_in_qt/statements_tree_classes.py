"""
fml
credits to Florian
"""

from PySide2.QtWidgets  import QApplication, QWidget
from PySide2.QtWidgets  import QTreeWidget, QTreeWidgetItem
from PySide2.QtCore     import Qt
from PySide2.QtGui      import QColor, QBrush, QIcon
from dataclasses import dataclass
import sys


@dataclass
class Statement:
    lean_name:      str
    pretty_name:    str
    identifier = 'Theorem 3.4'

    def pretty_hierarchy(self, outline):
        """
        Return the ordered (chapter > section > …) list of sections pretty
        names corresponding to where self is in the lean file. If the
        self.lean_name is 'rings_and_ideals.first_definitions.the_statement',
        return ['Rings and ideals', 'First definitions']. Most of the time
        outline will be present_course.outline, where present_course is the
        instance of Course which initiated self.

        :outline:   A dictionnary in which keys are hierarchy levels (e.g. 
                    'rings_and_ideals') and values are their pretty names
                    (e.g. 'Rings and ideals').
        :return:    The list of sections pretty names.
        """
        pretty_hierarchy = []

        def fkt(rmg_hierarchy):
            if not rmg_hierarchy:
                return
            else:
                pretty_hierarchy.insert(0, outline[rmg_hierarchy])
                # 'a.b.c.d' -> 'a.b.c'
                rmg_hierarchy = '.'.join(rmg_hierarchy.split('.')[:-1])
                fkt(rmg_hierarchy)

        name = '.'.join(self.lean_name.split('.')[:-1])
        fkt(name)

        return pretty_hierarchy


class StatementsTreeItem(QTreeWidgetItem):

    def __init__(self, titles):
        super().__init__(None, titles)
        self._initUI()

    def _initUI(self):
        self.setExpanded(True)
        # Print second col. in gray
        self.setForeground(1, QBrush(QColor('gray')))

    @classmethod
    def from_Statement(cls, statement):
        titles = [statement.pretty_name, statement.identifier]
        instance = cls(titles)

        return instance

class StatementsTreeNode(QTreeWidgetItem):

    def __init__(self, titles):
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
        super().__init__()
        self._initUI()
        self.init_tree(statements, outline)

    def _initUI(self):
        self.setAlternatingRowColors(True)
        self.setWindowTitle('StatementsTree')

    def addChild(self, item):
        """
        Usefull in self.init_branch_statement, do not delete!
        Usefull not to have to make a difference between self.addTopLevelItem
        when we add an item to the tree itself or parent.addChild when we add
        an item to a parent which is a tree item.
        """
        self.addTopLevelItem(item)

    def init_branch_statement(self, extg_tree, statement, branch, parent=None):
        """
        Add a branch to extg_tree and statement at the end of this branch.

        :extg_tree: A dictionnary that looks like this:
                    {'Groups': (StatementsTreeNode('Groups'),
                        {'Finite groups': (StatementsTreeNode(None, 'Finite
                                                                groups'),
                            {statement.text(0): (statement, dict()
                            )}
                        )}
                    )}
        :statement: An instance of StatementsTreeItem.
        :branch:    A branch (new or already existing) as a list of str, e.g.
                    ['Chapter', 'Section', 'Sub-section']. 
        :parent:    A StatementsTreeNode or extg_tree itself (at the first call
                    of the function). Either branch or statement is added as a
                    child of parent.
        """

        # If branch is empty, put statement at the end
        if not branch:
            item = StatementsTreeItem.from_Statement(statement)
            root = item.text(0)
            extg_tree[root] = (item, dict())
            parent.addChild(item)
            return 

        # Else go through the already existing branch or create the nodes
        root = branch[0]        # 'rings'
        branch = branch[1:]     # ['ideals', 'def']

        if not root in extg_tree: 
            extg_tree[root] = (StatementsTreeNode([root]), dict())
            parent.addChild(extg_tree[root][0])
        
        self.init_branch_statement(extg_tree[root][1], statement,
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

        :statements:    An ordered list of instances of the Statement class.
        :outline:       A dictionnary in which keys are hierarchy levels (e.g. 
                        'rings_and_ideals') and values are their pretty names
                        (e.g. 'Rings and ideals').
        """
        self.tree = dict()

        for statement in statements:
            branch = statement.pretty_hierarchy(outline)
            self.init_branch_statement(self.tree, statement, branch, self)

def test_pretty_hierarchy():

    outline = { 'groups': 'Groupes',
                'groups.finite_groups': 'Groupes finis'}

    statement = Statement('groups.finite_groups.lagrange_theorem',
                    'Théorème de Lagrange') 

    assert statement.pretty_hierarchy(outline) == ['Groupes', 'Groupes finis']
 

def test_launch_StatementsTree():

    arbre = [   'groups.definitions.sub_group',
                'groups.definitions.quotient',
                'groups.finite_groups.lagrange_theorem',
                'groups.finite_groups.Cauchy_theorem',
                'rings.definitions.sub_ring',
                'rings.definitions.ideal']

    statements = [  Statement('groups.definitions.sub_group',
                                'Définition sous-groupe'),
                    Statement('groups.definitions.quotient',
                                'Définition quotient'),
                    Statement('groups.finite_groups.lagrange_theorem',
                                'Théorème de Lagrange'),
                    Statement('groups.finite_groups.Cauchy_theorem',
                                'Théorème de Cauchy'),
                    Statement('rings.definitions.sub_ring',
                                'Définition sous-anneau'),
                    Statement('rings.definitions.ideal',
                                'Définition idéal')]

    outline = { 'groups': 'Groupes',
                'groups.definitions': 'Définitions',
                'groups.finite_groups': 'Groupes finis',
                'rings': 'Anneaux',
                'rings.definitions': 'Définitions'}

    app = QApplication(sys.argv)
    
    bush = StatementsTree(statements, outline)
    bush.resizeColumnToContents(0)
    bush.show()

    sys.exit(app.exec_())
