"""
fml
credits to Florian
"""

from PySide2.QtWidgets  import QApplication, QWidget
from PySide2.QtWidgets  import QTreeWidget, QTreeWidgetItem
from PySide2.QtCore     import Qt
from PySide2.QtGui      import QColor, QBrush, QIcon
from sys import exit

class StatementsTreeItem(QTreeWidgetItem):

    def __init__(self, parent, titles):
        super().__init__(parent, titles)
        self._initUI()

    def _initUI(self):
        self.setExpanded(True)
        # Print second col. in gray
        self.setForeground(1, QBrush(QColor('gray')))


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

    def __init__(self, data):
        super().__init__()
        self._initUI()
        self.initiate_tree(data)

    def _initUI(self):
        self.setAlternatingRowColors(True)
        self.setWindowTitle('StatementsTree')

    def addChild(self, item):
        self.addTopLevelItem(item)

    def initiate_branch(self, extg_tree, branch, parent=None):
        """
        Add a branch to self.tree (defined in self.initiate_tree). This
        item.tree is representend by a dict which to any node (str ID)
        associates a tuple containing :
        1.  its instance of QTreeWidgetItem (more specifically, StatementsTreeNode
            or StatementsTreeItem) ;
        2.  the next level of the branch as a dict with tuples
            (QTreeWidgetItem, dict) on the same principle.
        The function is recursive. The tree will always have < 100 leaves so
        performances will not be an issue.

        :extg_tree: Existing tree in which we wish to add our branch. A
                    dictionnary that looks like this:
                    {'groups': (QTreeWidgetItem(None, 'groups'),
                        {'sub_groups': (QTreeWidgetItem(None, 'sub_groups'),
                            {'def': (QTreeWidgetItem(None, 'def'),
                                dict()
                            )}
                        )}
                    )}
        :branch: A tree branch, e.g. ['rings', 'ideals', 'def'].
        :parent: A QTreeWidgetItem (more specifically an instance of StatementsTreeItem
                 or StatementsTreeNode) to which we will add a child / children.
        """

        if not branch:
            return

        root = branch[0]    # 'rings'
        remain = branch[1:] # ['ideals', 'def']

        if not root in extg_tree: 
            cls = StatementsTreeNode if remain else StatementsTreeItem
            extg_tree[root] = (cls(None, [root]), dict())
            parent.addChild(extg_tree[root][0])
        
        self.initiate_branch(extg_tree[root][1], remain, extg_tree[root][0])

    def initiate_tree(self, data):
        self.tree = dict()
        for branch in data:
            self.initiate_branch(self.tree, branch.split('.'), self)


def main():
    arbre = [   'groups.definitions.sub_group',
                'groups.definitions.quotient',
                'groups.finite_groups.lagrange_theorem',
                'groups.finite_groups.Cauchy_theorem',
                'rings.definitions.sub_ring',
                'rings.definitions.ideal']


    app = QApplication()
    
    buisson = StatementsTree(ARBRE)
    buisson.resizeColumnToContents(0)
    buisson.show()

    exit(app.exec_())


if __name__ == '__main__':
    main()
