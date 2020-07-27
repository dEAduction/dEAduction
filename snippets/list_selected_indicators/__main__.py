from functools import partial
import sys
from PySide2.QtCore import Slot
from PySide2.QtGui import QBrush, QColor
from PySide2.QtWidgets import (QApplication,
        QListWidget,
        QListWidgetItem,
        QHBoxLayout,
        QWidget,
        QPushButton)


class ListItem(QListWidgetItem):

    def __init__(self, text: str):
        super().__init__(text)
        self.is_selected = False

    def __eq__(self, other):
        return self is other

    def mark_selected(self, yes=True):
        if yes:
            brush = QBrush(QColor('limegreen'))
        else:
            brush = QBrush()

        self.is_selected = yes
        self.setBackground(brush)


class List(QListWidget):

    def __init__(self):
        super().__init__()
        self.current_selection = []

        # Two lists widget
        self.addItem(ListItem('Anthony'))
        self.addItem(ListItem('Chad'))
        self.addItem(ListItem('Flea'))
        self.addItem(ListItem('John'))

        # Signals
        self.itemDoubleClicked.connect(self.record_selection)

    def print_current_selection(self):

        print('Current selection: ',
                [item.text() for item in self.current_selection])

    @Slot()
    def record_selection(self):
        item = self.selectedItems()[0]
        item.setSelected(False)

        if (not item.is_selected) and (not item in self.current_selection):
            item.mark_selected(True)
            self.current_selection.append(item)
        elif item.is_selected:
            item.mark_selected(False)
            self.current_selection.remove(item)

        self.print_current_selection()

    @Slot()
    def clear_selection(self):
        for item in self.current_selection:
            item.mark_selected(False)

        self.current_selection = []
        self.print_current_selection()


class Container(QWidget):

    def __init__(self):
        super().__init__()
        self.list = List()
        self.clear_btn = QPushButton('Clear selection')
        
        self.clear_btn.clicked.connect(self.list.clear_selection)

        self.lyt = QHBoxLayout()
        self.lyt.addWidget(self.list)
        self.lyt.addWidget(self.clear_btn)
        self.setLayout(self.lyt)


if __name__ == '__main__':
    app = QApplication()

    c = Container()
    c.show()

    sys.exit(app.exec_())
