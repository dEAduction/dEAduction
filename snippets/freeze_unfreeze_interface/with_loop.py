from functools import partial
import logging
import sys
from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (
        QApplication,
        QListWidget,
        QListWidgetItem,
        QPushButton,
        QHBoxLayout,
        QVBoxLayout,
        QWidget)
import deaduction.pylib.logger as logger


class WetButton(QPushButton):

    def __init__(self, text):
        super().__init__(text)

    def set_clickable(self, yes=True):
        if yes:
            self.setEnabled(True)
        else:
            self.setEnabled(False)


class WetListItem(QListWidgetItem):

    def __init__(self, text):
        super().__init__()
        self.setText(text)

    def set_selectable(self, yes=True):
        if yes:
            new_flags = self.flags & Qt.ItemIsSelectable
        else:
            new_flags = self.flags & ~Qt.ItemIsSelectable

        self.setFlags(new_flags)


class WetSand(QWidget):

    def __init__(self):
        super().__init__()

        # Init list
        self.list = QListWidget()
        self.list.addItem(WetListItem("You don't form in the wet sand"))
        self.list.addItem(WetListItem("You don't form at all"))

        # Init buttons
        self.btns = [   WetButton('johs'),
                        WetButton('jon'),
                        WetButton('feel'),
                        WetButton('chat'),
                        WetButton('tony')]

        # Freeze and unfreeze buttons
        self.freeze_btn =    QPushButton('Freeze me')
        self.unfreeze_btn =  QPushButton('Unfreeze me')

        # Layout stuff
        self.btn_lyt = QVBoxLayout()
        for btn in self.btns:
            self.btn_lyt.addWidget(btn)

        self.top_lyt = QHBoxLayout()
        self.top_lyt.addWidget(self.list)
        self.top_lyt.addLayout(self.btn_lyt)

        self.bottom_lyt = QHBoxLayout()
        self.bottom_lyt.addWidget(self.freeze_btn)
        self.bottom_lyt.addWidget(self.unfreeze_btn)

        self.main_lyt = QVBoxLayout()
        self.main_lyt.addLayout(self.top_lyt)
        self.main_lyt.addLayout(self.bottom_lyt)

        # Signals and slots
        # Use functools.partial to send arguments
        self.freeze_btn.clicked.connect(partial(self.freeze, True))
        self.unfreeze_btn.clicked.connect(partial(self.freeze, False))

        # Don't forget me
        self.setLayout(self.main_lyt)
        self.show()

    @Slot()
    def freeze(self, yes=True):
        # Freeze buttons
        print(yes)
        btns = (self.btn_lyt.itemAt(i).widget() for i in range(self.btn_lyt.count()))
        for btn in btns:
            btn.set_clickable(not yes)

        # Freeze list items
        list_items = [self.list.item(i) for i in range(self.list.count())]
        for list_item in list_items:
            list_item.set_selectable(not yes)


if __name__ == '__main__':
    logger.configure()
    log = logging.getLogger(__name__)

    app = QApplication([])

    youdontformatall = WetSand()

    sys.exit(app.exec_())
