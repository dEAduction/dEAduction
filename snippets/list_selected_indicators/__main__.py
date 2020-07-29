import logging
from functools import partialmethod
import sys
from typing import List
import deaduction.pylib.logger as logger
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

    def __init__(self, suffixe):
        super().__init__()

        # Two lists widget
        self.addItem(ListItem('Anthony' + suffixe))
        self.addItem(ListItem('Chad' + suffixe))
        self.addItem(ListItem('Flea' + suffixe))
        self.addItem(ListItem('John' + suffixe))


class Container(QWidget):

    def __init__(self):
        super().__init__()
        self.current_selection = []
        self.list1 = List(' 1')
        self.list2 = List(' 2')
        self.clear_btn = QPushButton('Clear selection')
        
        self.lyt = QHBoxLayout()
        self.lyt.addWidget(self.list1)
        self.lyt.addWidget(self.list2)
        self.lyt.addWidget(self.clear_btn)
        self.setLayout(self.lyt)

        # Signals
        self.list1.itemClicked.connect(self.record_selection)
        self.list2.itemClicked.connect(self.record_selection)
        self.clear_btn.clicked.connect(self.clear_selection)

    def pretty_selection(self):

        return str([item.text() for item in self.current_selection])

    @Slot(ListItem)
    def record_selection(self, item: ListItem):
        log.debug('Recording selection')
        item.setSelected(False)

        if (not item.is_selected) and (not item in self.current_selection):
            item.mark_selected(True)
            self.current_selection.append(item)
        elif item.is_selected:
            item.mark_selected(False)
            self.current_selection.remove(item)

        log.debug(self.pretty_selection())

    @Slot()
    def clear_selection(self):
        for item in self.current_selection:
            item.mark_selected(False)

        self.current_selection = []

        log.debug(self.pretty_selection())


if __name__ == '__main__':
    logger.configure()
    log = logging.getLogger(__name__)

    app = QApplication()

    c = Container()
    c.show()

    sys.exit(app.exec_())
