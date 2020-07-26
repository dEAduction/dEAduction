import sys
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem


@Slot()
def slut():
    print('Slut')


class SlutTree(QTreeWidget):

    def __init__(self):
        super().__init__()

        john = QTreeWidgetItem(None, ['John'])
        josh = QTreeWidgetItem(None, ['Josh'])
        self.addTopLevelItem(john)
        self.addTopLevelItem(josh)

        self.itemDoubleClicked.connect(slut)

if __name__ == '__main__':
    app = QApplication()

    tree = SlutTree()
    tree.show()

    sys.exit(app.exec_())
