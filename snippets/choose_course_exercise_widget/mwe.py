import sys
from PySide2.QtWidgets import ( QApplication,
                                QLabel,
                                QTreeWidget,
                                QTreeWidgetItem, 
                                QVBoxLayout,
                                QWidget)


class DisclosureTree(QTreeWidget):

    def __init__(self):

        super().__init__()

        # Add content
        self.setColumnCount(1)
        parent_item = QTreeWidgetItem(self, ['Disclosure triangle'])
        self.addTopLevelItem(parent_item)
        parent_item.addChild(QTreeWidgetItem(parent_item, 'AAA'))
        parent_item.addChild(QTreeWidgetItem(parent_item, 'BBB'))
        parent_item.addChild(QTreeWidgetItem(parent_item, 'CCC'))

        # Cosmetics
        self.header().hide()
        self.setStyleSheet('background-color: transparent;')

if __name__ == '__main__':
    app = QApplication()

    vbox = QVBoxLayout()
    disclosuretree = DisclosureTree()
    label = QLabel('Plenty of space above…')
    vbox.addWidget(disclosuretree)
    vbox.addWidget(label)
    vbox.addStretch()

    widget = QWidget()
    widget.setLayout(vbox)
    widget.show()

    sys.exit(app.exec_())
