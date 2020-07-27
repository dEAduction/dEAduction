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

    def mark_selected(self, yes=True):
        if yes:
            brush = QBrush(QColor('chartreuse'))
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

    @Slot()
    def record_selection(self):
        selected_item = self.selectedItems()[0]
        selected_item.mark_selected()
        self.current_selection.append(selected_item)

    @Slot()
    def clear_selection(self):
        for item in self.current_selection:
            item.mark_selected(False)


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
