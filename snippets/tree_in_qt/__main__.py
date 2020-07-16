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

    def __init__(self, parent, titles):
        super().__init__(parent, titles)
        self._initUI()

    def _initUI(self):
        self.setExpanded(True)
        # Print second col. in gray
        self.setForeground(1, QBrush(QColor('gray')))

    @classmethod
    def from_Statement(cls, statement):
        titles = [statement.pretty_name, statement.identifier]
        instance = cls(None, titles)

        return instance

class StatementsTreeNode(QTreeWidgetItem):

    def __init__(self, parent, titles):
        super().__init__(parent, titles)
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
        self.addTopLevelItem(item)

    def init_branch_statement(self, extg_tree, statement, rmg_branch, parent=None):
        """
        Add a rmg_branch to self.tree (defined in self.init_tree). This
        item.tree is representend by a dict which to any node (str ID)
        associates a tuple containing :
        1.  its instance of QTreeWidgetItem (more specifically, StatementsTreeNode
            or StatementsTreeItem) ;
        2.  the next level of the rmg_branch as a dict with tuples
            (QTreeWidgetItem, dict) on the same principle.
        The function is recursive. The tree will always have < 100 leaves so
        performances will not be an issue.

        :extg_tree: Existing tree in which we wish to add our rmg_branch. A
                    dictionnary that looks like this:
                    {'groups': (QTreeWidgetItem(None, 'groups'),
                        {'sub_groups': (QTreeWidgetItem(None, 'sub_groups'),
                            {'def': (QTreeWidgetItem(None, 'def'),
                                dict()
                            )}
                        )}
                    )}
        :rmg_branch: A tree branch, e.g. ['rings', 'ideals', 'def'].
        :parent: A QTreeWidgetItem (more specifically an instance of StatementsTreeItem
                 or StatementsTreeNode) to which we will add a child / children.
        """

        if not rmg_branch:
            item = StatementsTreeItem.from_Statement(statement)
            parent.addChild(item)
            return 

        root = rmg_branch[0]        # 'rings'
        rmg_branch = rmg_branch[1:] # ['ideals', 'def']

        if not root in extg_tree: 
            extg_tree[root] = (StatementsTreeNode(None, [root]), dict())
            parent.addChild(extg_tree[root][0])
        
        self.init_branch_statement(extg_tree[root][1], statement, rmg_branch, extg_tree[root][0])

    def init_tree(self, statements, outline):
        self.tree = dict()

        for statement in statements:
            rmg_branch = statement.pretty_hierarchy(outline)
            self.init_branch_statement(self.tree, statement, rmg_branch, self)


ARBRE = [   'groups.definitions.sub_group',
            'groups.definitions.quotient',
            'groups.finite_groups.lagrange_theorem',
            'groups.finite_groups.Cauchy_theorem',
            'rings.definitions.sub_ring',
            'rings.definitions.ideal']

STATEMENTS = [  Statement('groups.definitions.sub_group',
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

OUTLINE = { 'groups': 'Groupes',
            'groups.definitions': 'Définitions',
            'groups.finite_groups': 'Groupes finis',
            'rings': 'Anneaux',
            'rings.definitions': 'Définitions'}

def main():

    app = QApplication(sys.argv)
    
    buisson = StatementsTree(STATEMENTS, OUTLINE)
    buisson.resizeColumnToContents(0)
    buisson.show()

    sys.exit(app.exec_())

def tests():
    s = Statement('groups.finite_groups.lagrange_theorem',
                    'Théorème de Lagrange') 

    assert s.pretty_hierarchy(OUTLINE) == ['Groupes', 'Groupes finis']

if __name__ == '__main__':
    tests()
    main()
