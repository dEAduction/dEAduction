"""
fml
credits to Florian
"""

from PySide2.QtWidgets  import QApplication, QWidget
from PySide2.QtWidgets  import QTreeWidget, QTreeWidgetItem
from PySide2.QtCore     import Qt
from PySide2.QtGui      import QColor, QBrush, QIcon
from sys import exit

BLAZES = ['Echtelion', 'Eugenie', 'Meige', 'Monheim', 'Princesse']
ROLES = ['Sous-chef', 'Ktarchiduc', 'Sous-chef', 'Some dude']
ARBRE = ['algebre.anneaux.definition',
            'algebre.anneaux.theoreme_factorisation',
            'algebre.noetherianite.transfert',
            'algebre.noetherianite.principal_implique_noetherien']


class Statement(QTreeWidgetItem):

    def __init__(self, parent, titles):
        super().__init__(parent, titles)
        self._initUI()

    def _initUI(self):
        self.setExpanded(True)
        # Print second col. in gray
        self.setForeground(1, QBrush(QColor('gray')))


class StatementsNode(QTreeWidgetItem):

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


class Buisson(QTreeWidget):

    def __init__(self, data):
        super().__init__()
        self._initUI()
        self.initiate_tree(data)

    def _initUI(self):
        self.setAlternatingRowColors(True)
        self.setWindowTitle('Buisson')
        self.show()

    def addChild(self, item):
        self.addTopLevelItem(item)

    def initiate_branch(self, node, path, parent=None):
        """
        En gros l'idée est d'avoir un dico qui à un niveau de la hiérarchie
        associe un tuple contenant l'instance du QTreeViewWidget
        correspondante, puis un autre dico contenant le prochain niveau sur le
        même principe (clé/tuple)

        toplevel = QTreeViewItem("toplevel")
        process_items(items, txt.split("."),parent=toplevel)

        :path: 
        """

        if not path:
            return

        root = path[0]
        remain = path[1:]

        if not root in node:
            cls = StatementsNode if remain else Statement
            node[root] = (cls(None, [root]), dict())
            if parent:
                parent.addChild(node[root][0])
        
        self.initiate_branch(node[root][1], remain, node[root][0])

    def initiate_tree(self, data):
        self.items = dict()
        for branch in data:
            self.initiate_branch(self.items, branch.split('.'), self)


def main():
    app = QApplication()
    
    buisson = Buisson(ARBRE)
    buisson.resizeColumnToContents(0)

    exit(app.exec_())


if __name__ == '__main__':
    main()
